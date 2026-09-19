(() => {
  'use strict';

  const config = window.ImpossibleLabLeaderboardConfig;
  const supabaseFactory = window.supabase?.createClient;
  const GAME_TITLES = Object.freeze({
    guess: 'Guess the Impossible',
    crossword: 'Cross the Impossible',
    alphabet: 'The Impossible Alphabet',
    spin: 'Spin the Impossible',
    timeline: 'Impossible Timeline',
    relics: 'Impossible Relics',
    origins: 'Impossible Origins',
    ascent: 'Impossible Ascent'
  });
  const LEVELS = Object.freeze(['explorer', 'analyst', 'impossible']);
  const LEVEL_LABELS = Object.freeze({ explorer: 'Explorer', analyst: 'Analyst', impossible: 'Impossible' });
  const SCORE_SCALE = 1000;
  const LAB_MAX = Object.keys(GAME_TITLES).length * SCORE_SCALE;
  const client = config && supabaseFactory
    ? supabaseFactory(config.url, config.publishableKey, {
      auth: { persistSession: true, autoRefreshToken: true, detectSessionInUrl: false },
      global: { headers: { 'X-Client-Info': 'lca-impossible-lab-leaderboard/1.0.0' } }
    })
    : null;

  let profilePromise = null;
  let pendingResult = null;
  const submitted = new Set();
  const mounts = new Set();

  const rounded = (value) => Math.round(Number.isFinite(Number(value)) ? Number(value) : 0);
  const clamp = (value, minimum, maximum) => Math.min(maximum, Math.max(minimum, value));
  const formatNumber = (value) => rounded(value).toLocaleString('en-US');

  const make = (tag, className, text) => {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (text !== undefined) element.textContent = text;
    return element;
  };

  const publicMessage = (error, fallback) => {
    const message = String(error?.message || '');
    if (/already in use|duplicate key/i.test(message)) return 'That nickname is already in use. Try another one.';
    if (/3.*20|nickname/i.test(message) && /characters|letters|invalid/i.test(message)) {
      return 'Use 3–20 characters: letters, numbers, spaces, hyphens or underscores.';
    }
    if (/anonymous.*disabled/i.test(message)) return 'Public ranking registration is temporarily unavailable.';
    if (/rate|limit/i.test(message)) return 'Too many score submissions. Please try again later.';
    return fallback;
  };

  const rpc = async (name, parameters = {}) => {
    if (!client) throw new Error('Leaderboard client unavailable');
    const { data, error } = await client.rpc(name, parameters);
    if (error) throw error;
    return Array.isArray(data) ? data : [];
  };

  const existingSession = async () => {
    if (!client) return null;
    const { data, error } = await client.auth.getSession();
    if (error) throw error;
    return data.session || null;
  };

  const ensureSession = async () => {
    const current = await existingSession();
    if (current) return current;
    const { data, error } = await client.auth.signInAnonymously();
    if (error) throw error;
    return data.session;
  };

  const getProfile = async ({ refresh = false } = {}) => {
    if (refresh) profilePromise = null;
    if (!client) return null;
    if (!profilePromise) {
      profilePromise = (async () => {
        const session = await existingSession();
        if (!session) return null;
        const rows = await rpc('get_my_lab_profile');
        return rows[0] || null;
      })().catch((error) => {
        profilePromise = null;
        throw error;
      });
    }
    return profilePromise;
  };

  const setNickname = async (nickname) => {
    await ensureSession();
    const rows = await rpc('set_lab_nickname', { p_nickname: nickname });
    profilePromise = Promise.resolve(rows[0] || null);
    return rows[0] || null;
  };

  const leaveLeaderboards = async () => {
    await rpc('leave_lab_leaderboards');
    await client.auth.signOut({ scope: 'local' });
    profilePromise = Promise.resolve(null);
    pendingResult = null;
  };

  const randomUuid = () => {
    if (window.crypto?.randomUUID) return window.crypto.randomUUID();
    const bytes = new Uint8Array(16);
    window.crypto.getRandomValues(bytes);
    bytes[6] = (bytes[6] & 0x0f) | 0x40;
    bytes[8] = (bytes[8] & 0x3f) | 0x80;
    const hex = [...bytes].map((value) => value.toString(16).padStart(2, '0')).join('');
    return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-${hex.slice(12, 16)}-${hex.slice(16, 20)}-${hex.slice(20)}`;
  };

  const fetchGame = (gameId, level) => rpc('get_game_leaderboard', {
    p_game_id: gameId,
    p_difficulty: level,
    p_limit: 10,
    p_offset: 0
  });

  const fetchLab = () => rpc('get_lab_leaderboard', { p_limit: 10, p_offset: 0 });

  const fetchMyRanks = (gameId, level) => rpc('get_my_lab_ranks', {
    p_game_id: gameId || 'guess',
    p_difficulty: level || 'analyst'
  });

  const submit = async (result) => {
    if (!result || submitted.has(result.submissionId)) return null;
    const profile = await getProfile();
    if (!profile) return null;
    const rows = await rpc('submit_lab_score', {
      p_submission_id: result.submissionId,
      p_game_id: result.gameId,
      p_difficulty: result.level,
      p_score: result.score,
      p_maximum: result.maximum,
      p_completion: result.completion,
      p_accuracy: result.accuracy
    });
    submitted.add(result.submissionId);
    return rows[0] || null;
  };

  const renderRows = (list, rows, type) => {
    list.replaceChildren();
    if (!rows.length) {
      const empty = make('li', 'lab-leaderboard-empty', 'No ranked results yet. Be the first analyst on the board.');
      list.appendChild(empty);
      return;
    }
    const fragment = document.createDocumentFragment();
    rows.forEach((row) => {
      const item = make('li', 'lab-leaderboard-row');
      const rank = make('span', 'lab-leaderboard-rank', `#${formatNumber(row.rank)}`);
      const identity = make('strong', 'lab-leaderboard-name', row.nickname);
      const score = make('span', 'lab-leaderboard-value');
      if (type === 'lab') {
        score.textContent = `${formatNumber(row.lab_score)} / ${formatNumber(LAB_MAX)}`;
        const detail = make('small', '', `${formatNumber(row.experiments_completed)} / 7 experiments`);
        score.appendChild(detail);
      } else {
        score.textContent = `${formatNumber(row.normalized)} / ${formatNumber(SCORE_SCALE)}`;
        const detail = make('small', '', `${formatNumber(row.score)} / ${formatNumber(row.maximum)} game pts`);
        score.appendChild(detail);
      }
      item.append(rank, identity, score);
      fragment.appendChild(item);
    });
    list.appendChild(fragment);
  };

  const renderIdentity = async (host, status, onChanged) => {
    host.replaceChildren();
    if (!client) {
      host.appendChild(make('p', 'lab-leaderboard-unavailable', 'Public rankings are unavailable. Local records continue to work normally.'));
      return;
    }

    let profile = null;
    try {
      profile = await getProfile();
    } catch (error) {
      host.appendChild(make('p', 'lab-leaderboard-unavailable', 'Could not load the ranking profile. Local records remain available.'));
      return;
    }

    const copy = make('div', 'lab-leaderboard-identity-copy');
    const eyebrow = make('p', 'eyebrow', profile ? 'PUBLIC PROFILE' : 'OPTIONAL PUBLIC PROFILE');
    const title = make('h3', '', profile ? `Playing as ${profile.nickname}` : 'Choose a ranking nickname');
    const description = make('p', '', profile
      ? 'New completed results are published automatically. Your device-local records remain separate.'
      : 'Join with a public nickname. No email is required; existing local records stay private and only future completed results are published.');
    copy.append(eyebrow, title, description);

    const form = make('form', 'lab-leaderboard-form');
    const label = make('label', '', profile ? 'Update nickname' : 'Public nickname');
    const input = document.createElement('input');
    input.type = 'text';
    input.name = 'nickname';
    input.autocomplete = 'nickname';
    input.minLength = 3;
    input.maxLength = 20;
    input.pattern = '[A-Za-z0-9][A-Za-z0-9 _-]{2,19}';
    input.required = true;
    input.placeholder = 'e.g. CarbonSleuth';
    if (profile) input.value = profile.nickname;
    label.appendChild(input);
    const submitButton = make('button', 'button', profile ? 'Update nickname' : 'Join rankings');
    submitButton.type = 'submit';
    form.append(label, submitButton);

    if (profile) {
      const leaveButton = make('button', 'button secondary lab-leaderboard-leave', 'Leave rankings');
      leaveButton.type = 'button';
      leaveButton.addEventListener('click', async () => {
        if (!window.confirm('Remove your public profile and all public scores? Local browser records will not be deleted.')) return;
        leaveButton.disabled = true;
        status.textContent = 'Removing public ranking data…';
        try {
          await leaveLeaderboards();
          status.textContent = 'Public profile removed. Local records are unchanged.';
          await onChanged?.();
        } catch (error) {
          status.textContent = 'Could not remove the public profile. Please try again.';
          leaveButton.disabled = false;
        }
      });
      form.appendChild(leaveButton);
    }

    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      submitButton.disabled = true;
      status.textContent = profile ? 'Updating nickname…' : 'Creating anonymous ranking profile…';
      try {
        await setNickname(input.value);
        if (pendingResult) await submit(pendingResult);
        status.textContent = pendingResult
          ? 'Profile saved and the latest completed result was published.'
          : 'Profile saved. Future completed results will be published automatically.';
        await onChanged?.();
      } catch (error) {
        status.textContent = publicMessage(error, 'Could not save the nickname. Please try again.');
        submitButton.disabled = false;
      }
    });

    host.append(copy, form);
  };

  const createBoard = ({ type, gameId, level = 'analyst', title, description }) => {
    const section = make('section', `lab-leaderboard-panel is-${type}`);
    section.dataset.leaderboardType = type;
    const header = make('header', 'lab-leaderboard-header');
    const heading = make('div');
    heading.append(make('p', 'eyebrow', type === 'lab' ? 'PUBLIC ANALYST RANKING' : 'PUBLIC GAME RANKING'));
    heading.append(make('h2', '', title));
    heading.append(make('p', '', description));
    header.appendChild(heading);

    const tabs = make('div', 'lab-leaderboard-tabs');
    if (type === 'game') {
      tabs.setAttribute('aria-label', 'Leaderboard difficulty');
      LEVELS.forEach((candidate) => {
        const button = make('button', 'lab-leaderboard-tab', LEVEL_LABELS[candidate]);
        button.type = 'button';
        button.dataset.level = candidate;
        button.setAttribute('aria-pressed', String(candidate === level));
        tabs.appendChild(button);
      });
      header.appendChild(tabs);
    }

    const identity = make('div', 'lab-leaderboard-identity');
    const status = make('p', 'lab-leaderboard-status', 'Loading public rankings…');
    status.setAttribute('aria-live', 'polite');
    const list = make('ol', 'lab-leaderboard-list');
    list.setAttribute('aria-label', title);
    section.append(header, identity, status, list);

    let selectedLevel = level;
    const refresh = async () => {
      status.textContent = 'Loading public rankings…';
      try {
        const rows = type === 'lab' ? await fetchLab() : await fetchGame(gameId, selectedLevel);
        renderRows(list, rows, type);
        let rankingNote = '';
        const profile = await getProfile();
        if (profile) {
          const myRows = await fetchMyRanks(gameId, selectedLevel);
          const mine = myRows[0];
          if (type === 'lab' && mine?.lab_rank) {
            rankingNote = ` Your Lab rank is #${formatNumber(mine.lab_rank)} of ${formatNumber(mine.lab_total)}.`;
          } else if (type === 'game' && mine?.game_rank) {
            rankingNote = ` Your ${LEVEL_LABELS[selectedLevel]} rank is #${formatNumber(mine.game_rank)} of ${formatNumber(mine.game_total)}.`;
          }
        }
        status.textContent = (rows.length
          ? `Showing the top ${rows.length} public record${rows.length === 1 ? '' : 's'}.`
          : 'The public board is ready for its first result.') + rankingNote;
      } catch (error) {
        list.replaceChildren();
        status.textContent = 'Public rankings could not be loaded. Local records continue to work normally.';
      }
      await renderIdentity(identity, status, async () => {
        await refresh();
        mounts.forEach((mount) => {
          if (mount !== refresh) void mount();
        });
      });
    };

    tabs.querySelectorAll('button').forEach((button) => {
      button.addEventListener('click', () => {
        selectedLevel = button.dataset.level;
        tabs.querySelectorAll('button').forEach((candidate) => {
          candidate.setAttribute('aria-pressed', String(candidate === button));
        });
        void refresh();
      });
    });

    mounts.add(refresh);
    return { section, refresh, status, gameId, level: () => selectedLevel };
  };

  const mountHub = () => {
    const host = document.querySelector('[data-lab-global-leaderboard]');
    if (!host) return null;
    const board = createBoard({
      type: 'lab',
      title: 'Impossible Lab leaderboard',
      description: 'The sum of each player’s eight best normalized Analyst results, up to 8,000 points.'
    });
    host.replaceChildren(board.section);
    void board.refresh();
    return board;
  };

  const mountGame = () => {
    const gameId = document.body?.dataset?.labGame;
    const shell = document.querySelector('main .lab-shell');
    if (!gameId || !shell || !GAME_TITLES[gameId]) return null;
    const currentLevel = window.ImpossibleLabDifficulty?.current?.() || 'analyst';
    const board = createBoard({
      type: 'game',
      gameId,
      level: currentLevel,
      title: `${GAME_TITLES[gameId]} leaderboard`,
      description: 'Best normalized game performance by difficulty. Environmental results are never compared.'
    });
    const noscript = shell.querySelector('noscript');
    if (noscript) shell.insertBefore(board.section, noscript);
    else shell.appendChild(board.section);
    void board.refresh();
    return board;
  };

  let gameBoard = null;

  const handleResult = async (summary = {}) => {
    if (!client || !GAME_TITLES[summary.gameId] || summary.persist === false) return null;
    const payload = {
      submissionId: randomUuid(),
      gameId: summary.gameId,
      level: LEVELS.includes(summary.level) ? summary.level : 'analyst',
      score: Math.max(0, rounded(summary.score)),
      maximum: Math.max(1, rounded(summary.maximum)),
      completion: clamp(rounded(summary.completion), 0, 100),
      accuracy: clamp(rounded(summary.accuracy), 0, 100)
    };
    pendingResult = payload;
    try {
      const profile = await getProfile();
      if (!profile) {
        if (gameBoard?.status) gameBoard.status.textContent = 'Result saved locally. Choose a nickname below to publish it.';
        return null;
      }
      if (gameBoard?.status) gameBoard.status.textContent = 'Publishing completed result…';
      const result = await submit(payload);
      pendingResult = null;
      await gameBoard?.refresh();
      return result;
    } catch (error) {
      if (gameBoard?.status) gameBoard.status.textContent = publicMessage(error, 'The result remains local because it could not be published.');
      return null;
    }
  };

  const initialize = () => {
    mountHub();
    gameBoard = mountGame();
  };

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initialize, { once: true });
  else initialize();

  window.ImpossibleLabLeaderboard = Object.freeze({
    available: Boolean(client),
    getProfile,
    setNickname,
    fetchGame,
    fetchLab,
    fetchMyRanks,
    handleResult
  });
})();
