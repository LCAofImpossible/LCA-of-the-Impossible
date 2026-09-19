begin;

alter table public.lab_games drop constraint lab_games_game_number_check;
alter table public.lab_games add constraint lab_games_game_number_check check (game_number between 1 and 8);

insert into public.lab_games (id, game_number, title, active) values
  ('ascent', 8, 'Impossible Ascent', true)
on conflict (id) do update set game_number = excluded.game_number, title = excluded.title, active = excluded.active;

create or replace function public.submit_lab_score(
  p_submission_id uuid,
  p_game_id text,
  p_difficulty text,
  p_score integer,
  p_maximum integer,
  p_completion integer,
  p_accuracy integer
)
returns table (
  accepted boolean,
  best_score integer,
  best_maximum integer,
  best_normalized integer,
  plays integer
)
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_user_id uuid := (select auth.uid());
  v_submission_pk bigint;
  v_normalized integer;
  v_accepted boolean := false;
begin
  if v_user_id is null then
    raise exception using errcode = '42501', message = 'Authentication is required.';
  end if;

  if not exists (
    select 1 from public.lab_players as p
    where p.user_id = v_user_id and p.active
  ) then
    raise exception using errcode = '42501', message = 'Choose a public nickname before submitting a score.';
  end if;

  if not exists (
    select 1 from public.lab_games as g
    where g.id = p_game_id and g.active
  ) then
    raise exception using errcode = '22023', message = 'Unknown Lab game.';
  end if;

  if p_difficulty not in ('explorer', 'analyst', 'impossible') then
    raise exception using errcode = '22023', message = 'Unknown difficulty.';
  end if;

  if p_score is null or p_maximum is null or p_maximum <= 0
     or p_score < 0 or p_score > p_maximum or p_maximum > 100000
     or p_completion not between 0 and 100
     or p_accuracy not between 0 and 100 then
    raise exception using errcode = '22023', message = 'Invalid score payload.';
  end if;

  if not (
    (p_game_id = 'guess' and p_maximum = 500)
    or (p_game_id = 'crossword' and p_difficulty = 'explorer' and p_maximum in (300, 350, 400))
    or (p_game_id = 'crossword' and p_difficulty = 'analyst' and p_maximum in (400, 450, 500))
    or (p_game_id = 'crossword' and p_difficulty = 'impossible' and p_maximum in (500, 550, 600))
    or (p_game_id = 'alphabet' and p_difficulty = 'explorer' and p_maximum = 2150)
    or (p_game_id = 'alphabet' and p_difficulty in ('analyst', 'impossible') and p_maximum = 3350)
    or (p_game_id = 'spin' and p_maximum between 500 and 25000)
    or (p_game_id = 'timeline' and p_difficulty = 'explorer' and p_maximum = 1200)
    or (p_game_id = 'timeline' and p_difficulty = 'analyst' and p_maximum = 3000)
    or (p_game_id = 'timeline' and p_difficulty = 'impossible' and p_maximum = 5000)
    or (p_game_id = 'relics' and p_difficulty = 'explorer' and p_maximum = 400)
    or (p_game_id = 'relics' and p_difficulty = 'analyst' and p_maximum = 600)
    or (p_game_id = 'relics' and p_difficulty = 'impossible' and p_maximum = 800)
    or (p_game_id = 'origins' and p_difficulty = 'explorer' and p_maximum = 2000)
    or (p_game_id = 'origins' and p_difficulty = 'analyst' and p_maximum = 2500)
    or (p_game_id = 'origins' and p_difficulty = 'impossible' and p_maximum = 3000)
    or (p_game_id = 'ascent' and p_difficulty = 'explorer' and p_maximum = 800)
    or (p_game_id = 'ascent' and p_difficulty = 'analyst' and p_maximum = 1200)
    or (p_game_id = 'ascent' and p_difficulty = 'impossible' and p_maximum = 1500)
  ) then
    raise exception using errcode = '22023', message = 'Score maximum does not match this game and difficulty.';
  end if;

  if exists (
    select 1 from public.lab_score_submissions as s
    where s.user_id = v_user_id and s.submission_id = p_submission_id
  ) then
    return query
      select false, b.best_score, b.best_score_maximum, b.best_normalized, b.plays
      from public.lab_player_bests as b
      where b.user_id = v_user_id
        and b.game_id = p_game_id
        and b.difficulty = p_difficulty;
    return;
  end if;

  if (
    select count(*)
    from public.lab_score_submissions as s
    where s.user_id = v_user_id
      and s.created_at >= now() - interval '1 hour'
  ) >= 30 then
    raise exception using errcode = 'P0001', message = 'Score submission limit reached. Try again later.';
  end if;

  insert into public.lab_score_submissions (
    submission_id, user_id, game_id, difficulty, score, maximum, completion, accuracy
  ) values (
    p_submission_id, v_user_id, p_game_id, p_difficulty,
    p_score, p_maximum, p_completion, p_accuracy
  )
  returning id, normalized into v_submission_pk, v_normalized;

  v_accepted := v_submission_pk is not null;

  insert into public.lab_player_bests (
    user_id, game_id, difficulty,
    best_score, best_score_maximum,
    rank_score, rank_maximum, best_normalized,
    best_normalized_at, plays, updated_at
  ) values (
    v_user_id, p_game_id, p_difficulty,
    p_score, p_maximum,
    p_score, p_maximum, v_normalized,
    now(), 1, now()
  )
  on conflict (user_id, game_id, difficulty) do update set
    best_score_maximum = case
      when excluded.best_score > public.lab_player_bests.best_score
        then excluded.best_score_maximum
      else public.lab_player_bests.best_score_maximum
    end,
    best_score = greatest(public.lab_player_bests.best_score, excluded.best_score),
    rank_score = case
      when excluded.best_normalized > public.lab_player_bests.best_normalized
        or (
          excluded.best_normalized = public.lab_player_bests.best_normalized
          and excluded.rank_score > public.lab_player_bests.rank_score
        ) then excluded.rank_score
      else public.lab_player_bests.rank_score
    end,
    rank_maximum = case
      when excluded.best_normalized > public.lab_player_bests.best_normalized
        or (
          excluded.best_normalized = public.lab_player_bests.best_normalized
          and excluded.rank_score > public.lab_player_bests.rank_score
        ) then excluded.rank_maximum
      else public.lab_player_bests.rank_maximum
    end,
    best_normalized_at = case
      when excluded.best_normalized > public.lab_player_bests.best_normalized
        then excluded.best_normalized_at
      else public.lab_player_bests.best_normalized_at
    end,
    best_normalized = greatest(public.lab_player_bests.best_normalized, excluded.best_normalized),
    plays = public.lab_player_bests.plays + 1,
    updated_at = now();

  return query
    select v_accepted, b.best_score, b.best_score_maximum, b.best_normalized, b.plays
    from public.lab_player_bests as b
    where b.user_id = v_user_id
      and b.game_id = p_game_id
      and b.difficulty = p_difficulty;
end;
$$;


commit;
