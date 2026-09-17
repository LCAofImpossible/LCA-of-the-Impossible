begin;

create table public.lab_games (
  id text primary key,
  game_number smallint not null unique check (game_number between 1 and 7),
  title text not null,
  active boolean not null default true
);

insert into public.lab_games (id, game_number, title, active) values
  ('guess', 1, 'Guess the Impossible', true),
  ('crossword', 2, 'Cross the Impossible', true),
  ('alphabet', 3, 'The Impossible Alphabet', true),
  ('spin', 4, 'Spin the Impossible', true),
  ('timeline', 5, 'Impossible Timeline', true),
  ('relics', 6, 'Impossible Relics', true),
  ('origins', 7, 'Impossible Origins', true)
on conflict (id) do update set
  game_number = excluded.game_number,
  title = excluded.title,
  active = excluded.active;

create table public.lab_players (
  user_id uuid primary key references auth.users(id) on delete cascade,
  nickname text not null,
  active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint lab_players_nickname_format_check check (
    nickname = btrim(nickname)
    and char_length(nickname) between 3 and 20
    and nickname ~ '^[A-Za-z0-9][A-Za-z0-9 _-]{2,19}$'
  )
);

create unique index lab_players_nickname_lower_uidx
  on public.lab_players ((lower(nickname)));

create table public.lab_score_submissions (
  id bigint generated always as identity primary key,
  submission_id uuid not null,
  user_id uuid not null references auth.users(id) on delete cascade,
  game_id text not null references public.lab_games(id),
  difficulty text not null check (difficulty in ('explorer', 'analyst', 'impossible')),
  score integer not null check (score between 0 and 100000),
  maximum integer not null check (maximum between 1 and 100000),
  normalized integer generated always as (
    round(least(greatest(score::numeric / maximum::numeric, 0), 1) * 1000)::integer
  ) stored,
  completion smallint not null check (completion between 0 and 100),
  accuracy smallint not null check (accuracy between 0 and 100),
  created_at timestamptz not null default now(),
  constraint lab_score_submissions_score_not_above_maximum_check check (score <= maximum),
  constraint lab_score_submissions_user_token_key unique (user_id, submission_id)
);

create index lab_score_submissions_user_created_idx
  on public.lab_score_submissions (user_id, created_at desc);
create index lab_score_submissions_game_rank_idx
  on public.lab_score_submissions (game_id, difficulty, normalized desc, created_at asc);

create table public.lab_player_bests (
  user_id uuid not null references auth.users(id) on delete cascade,
  game_id text not null references public.lab_games(id),
  difficulty text not null check (difficulty in ('explorer', 'analyst', 'impossible')),
  best_score integer not null check (best_score between 0 and 100000),
  best_score_maximum integer not null check (best_score_maximum between 1 and 100000),
  rank_score integer not null check (rank_score between 0 and 100000),
  rank_maximum integer not null check (rank_maximum between 1 and 100000),
  best_normalized integer not null check (best_normalized between 0 and 1000),
  best_normalized_at timestamptz not null default now(),
  plays integer not null default 1 check (plays > 0),
  updated_at timestamptz not null default now(),
  primary key (user_id, game_id, difficulty)
);

create index lab_player_bests_game_rank_idx
  on public.lab_player_bests (game_id, difficulty, best_normalized desc, best_normalized_at asc);
create index lab_player_bests_user_difficulty_idx
  on public.lab_player_bests (user_id, difficulty);

alter table public.lab_games enable row level security;
alter table public.lab_players enable row level security;
alter table public.lab_score_submissions enable row level security;
alter table public.lab_player_bests enable row level security;

create policy "Public reads active Lab games"
  on public.lab_games
  for select
  to anon, authenticated
  using (active);

create policy "Deny direct access to Lab players"
  on public.lab_players
  for all
  to anon, authenticated
  using (false)
  with check (false);

create policy "Deny direct access to Lab submissions"
  on public.lab_score_submissions
  for all
  to anon, authenticated
  using (false)
  with check (false);

create policy "Deny direct access to Lab bests"
  on public.lab_player_bests
  for all
  to anon, authenticated
  using (false)
  with check (false);

revoke all on public.lab_players from public, anon, authenticated;
revoke all on public.lab_score_submissions from public, anon, authenticated;
revoke all on public.lab_player_bests from public, anon, authenticated;
revoke all on sequence public.lab_score_submissions_id_seq from public, anon, authenticated;
grant select on public.lab_games to anon, authenticated;

create or replace function public.set_lab_nickname(p_nickname text)
returns table (nickname text, created_at timestamptz, updated_at timestamptz)
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_user_id uuid := (select auth.uid());
  v_nickname text := btrim(p_nickname);
begin
  if v_user_id is null then
    raise exception using errcode = '42501', message = 'Authentication is required.';
  end if;

  if v_nickname is null
     or char_length(v_nickname) not between 3 and 20
     or v_nickname !~ '^[A-Za-z0-9][A-Za-z0-9 _-]{2,19}$' then
    raise exception using errcode = '22023', message = 'Nickname must be 3–20 characters and use letters, numbers, spaces, hyphens or underscores.';
  end if;

  begin
    insert into public.lab_players (user_id, nickname)
    values (v_user_id, v_nickname)
    on conflict (user_id) do update
      set nickname = excluded.nickname,
          active = true,
          updated_at = now();
  exception when unique_violation then
    raise exception using errcode = '23505', message = 'This nickname is already in use.';
  end;

  return query
    select p.nickname, p.created_at, p.updated_at
    from public.lab_players as p
    where p.user_id = v_user_id;
end;
$$;

create or replace function public.get_my_lab_profile()
returns table (nickname text, created_at timestamptz, updated_at timestamptz)
language sql
stable
security definer
set search_path = ''
as $$
  select p.nickname, p.created_at, p.updated_at
  from public.lab_players as p
  where p.user_id = (select auth.uid())
    and p.active;
$$;

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

create or replace function public.get_game_leaderboard(
  p_game_id text,
  p_difficulty text default 'analyst',
  p_limit integer default 10,
  p_offset integer default 0
)
returns table (
  rank bigint,
  nickname text,
  score integer,
  maximum integer,
  normalized integer,
  plays integer,
  achieved_at timestamptz
)
language sql
stable
security definer
set search_path = ''
as $$
  with ranked as (
    select
      row_number() over (
        order by b.best_normalized desc, b.best_normalized_at asc, lower(p.nickname) asc
      ) as rank,
      p.nickname,
      b.rank_score as score,
      b.rank_maximum as maximum,
      b.best_normalized as normalized,
      b.plays,
      b.best_normalized_at as achieved_at
    from public.lab_player_bests as b
    join public.lab_players as p on p.user_id = b.user_id and p.active
    join public.lab_games as g on g.id = b.game_id and g.active
    where b.game_id = p_game_id
      and b.difficulty = p_difficulty
  )
  select r.rank, r.nickname, r.score, r.maximum, r.normalized, r.plays, r.achieved_at
  from ranked as r
  order by r.rank
  limit least(greatest(coalesce(p_limit, 10), 1), 50)
  offset greatest(coalesce(p_offset, 0), 0);
$$;

create or replace function public.get_lab_leaderboard(
  p_limit integer default 10,
  p_offset integer default 0
)
returns table (
  rank bigint,
  nickname text,
  lab_score integer,
  experiments_completed integer,
  last_improved_at timestamptz
)
language sql
stable
security definer
set search_path = ''
as $$
  with totals as (
    select
      b.user_id,
      sum(b.best_normalized)::integer as lab_score,
      count(*)::integer as experiments_completed,
      max(b.best_normalized_at) as last_improved_at
    from public.lab_player_bests as b
    join public.lab_games as g on g.id = b.game_id and g.active
    where b.difficulty = 'analyst'
    group by b.user_id
  ), ranked as (
    select
      row_number() over (
        order by t.lab_score desc, t.experiments_completed desc, t.last_improved_at asc, lower(p.nickname) asc
      ) as rank,
      p.nickname,
      t.lab_score,
      t.experiments_completed,
      t.last_improved_at
    from totals as t
    join public.lab_players as p on p.user_id = t.user_id and p.active
  )
  select r.rank, r.nickname, r.lab_score, r.experiments_completed, r.last_improved_at
  from ranked as r
  order by r.rank
  limit least(greatest(coalesce(p_limit, 10), 1), 50)
  offset greatest(coalesce(p_offset, 0), 0);
$$;

create or replace function public.get_my_lab_ranks(
  p_game_id text,
  p_difficulty text default 'analyst'
)
returns table (
  game_rank bigint,
  game_total bigint,
  lab_rank bigint,
  lab_total bigint,
  lab_score integer,
  experiments_completed integer
)
language sql
stable
security definer
set search_path = ''
as $$
  with game_rows as (
    select
      b.user_id,
      row_number() over (
        order by b.best_normalized desc, b.best_normalized_at asc, lower(p.nickname) asc
      ) as rank
    from public.lab_player_bests as b
    join public.lab_players as p on p.user_id = b.user_id and p.active
    where b.game_id = p_game_id and b.difficulty = p_difficulty
  ), totals as (
    select
      b.user_id,
      sum(b.best_normalized)::integer as score,
      count(*)::integer as completed,
      max(b.best_normalized_at) as improved_at
    from public.lab_player_bests as b
    join public.lab_games as g on g.id = b.game_id and g.active
    where b.difficulty = 'analyst'
    group by b.user_id
  ), lab_rows as (
    select
      t.user_id,
      t.score,
      t.completed,
      row_number() over (
        order by t.score desc, t.completed desc, t.improved_at asc, lower(p.nickname) asc
      ) as rank
    from totals as t
    join public.lab_players as p on p.user_id = t.user_id and p.active
  )
  select
    (select g.rank from game_rows as g where g.user_id = (select auth.uid())),
    (select count(*) from game_rows),
    (select l.rank from lab_rows as l where l.user_id = (select auth.uid())),
    (select count(*) from lab_rows),
    coalesce((select l.score from lab_rows as l where l.user_id = (select auth.uid())), 0),
    coalesce((select l.completed from lab_rows as l where l.user_id = (select auth.uid())), 0);
$$;

create or replace function public.leave_lab_leaderboards()
returns boolean
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_user_id uuid := (select auth.uid());
begin
  if v_user_id is null then
    raise exception using errcode = '42501', message = 'Authentication is required.';
  end if;

  delete from public.lab_score_submissions where user_id = v_user_id;
  delete from public.lab_player_bests where user_id = v_user_id;
  delete from public.lab_players where user_id = v_user_id;
  return true;
end;
$$;

revoke all on function public.set_lab_nickname(text) from public, anon;
revoke all on function public.get_my_lab_profile() from public, anon;
revoke all on function public.submit_lab_score(uuid, text, text, integer, integer, integer, integer) from public, anon;
revoke all on function public.get_game_leaderboard(text, text, integer, integer) from public;
revoke all on function public.get_lab_leaderboard(integer, integer) from public;
revoke all on function public.get_my_lab_ranks(text, text) from public, anon;
revoke all on function public.leave_lab_leaderboards() from public, anon;

grant execute on function public.set_lab_nickname(text) to authenticated;
grant execute on function public.get_my_lab_profile() to authenticated;
grant execute on function public.submit_lab_score(uuid, text, text, integer, integer, integer, integer) to authenticated;
grant execute on function public.get_game_leaderboard(text, text, integer, integer) to anon, authenticated;
grant execute on function public.get_lab_leaderboard(integer, integer) to anon, authenticated;
grant execute on function public.get_my_lab_ranks(text, text) to authenticated;
grant execute on function public.leave_lab_leaderboards() to authenticated;

comment on table public.lab_players is 'Public-nickname identities for Impossible Lab leaderboards. Direct client access is denied; use RPC functions.';
comment on table public.lab_score_submissions is 'Append-only accepted Impossible Lab results. Normalized score is calculated by PostgreSQL.';
comment on table public.lab_player_bests is 'Best per-player result for each game and difficulty, maintained only by submit_lab_score.';

notify pgrst, 'reload schema';

commit;
