import React from 'react';
import {
  AbsoluteFill,
  Audio,
  Img,
  OffthreadVideo,
  Sequence,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';

export type JudgeFilmProps = {
  useNarration: boolean;
  useLiveFootage: boolean;
  useHyperframes: boolean;
  useBandwidthProof: boolean;
};

export const judgeFilmSchemaDefaults: JudgeFilmProps = {
  useNarration: false,
  useLiveFootage: false,
  useHyperframes: false,
  useBandwidthProof: false,
};

// Duration lock v0.2.
// 235 seconds (3:55) keeps the judge film comfortably below the 5-minute
// submission ceiling while preserving ~58% live-product footage from the
// four planned evidence clips (137 seconds total).
export const JUDGE_FILM_SECONDS = 235;

const fps = 30;
const sec = (value: number) => Math.round(value * fps);

const palette = {
  paper: '#f2efe7',
  ink: '#161814',
  muted: '#697067',
  signal: '#ef5b3f',
  safe: '#2f785f',
  review: '#7657a6',
  line: 'rgba(22,24,20,.16)',
};

const segments = [
  {id: 'hook', start: 0, duration: 10, title: 'A correction should not create a second operational truth.', kicker: 'TRANSIT OPERATIONS'},
  {id: 'problem', start: 10, duration: 14, title: 'Controllers already juggle radio, maps and incidents.', kicker: 'THE FAILURE MODE'},
  {id: 'live-core', start: 24, duration: 86, title: 'Live voice → preview → Apply → same change identity', kicker: 'LIVE PRODUCT'},
  {id: 'negative', start: 110, duration: 35, title: 'Incomplete speech can be visible without becoming canonical.', kicker: 'NEGATIVE PATH'},
  {id: 'authority', start: 145, duration: 29, title: 'Stale review: refused. Current review: committed.', kicker: 'AUTHORITY'},
  {id: 'sponsor', start: 174, duration: 20, title: 'AssemblyAI is load-bearing in the speech path.', kicker: 'APPLICATION OF TECHNOLOGY'},
  {id: 'consequence', start: 194, duration: 16, title: 'GTFS-RT is regenerated and independently decoded.', kicker: 'REAL CONSEQUENCE'},
  {id: 'business', start: 210, duration: 14, title: 'Hands-free speed without probabilistic mutation authority.', kicker: 'BUSINESS VALUE'},
  {id: 'truth', start: 224, duration: 11, title: 'Speech is fast and fallible. ERRATA keeps one operational truth.', kicker: 'ERRATA'},
] as const;

// External narration stays out of the live-product block so the recorded
// browser audio (operator + real ERRATA AI33 guidance) remains intelligible.
const narration = [
  {start: 0, file: 'audio/01-intro.mp3'},
  {start: 174, file: 'audio/05-architecture.mp3'},
  {start: 194, file: 'audio/06-consequence.mp3'},
  {start: 210, file: 'audio/07-business.mp3'},
  {start: 224, file: 'audio/08-close.mp3'},
] as const;

const fallbackNarration = [
  {start: 24, file: 'audio/02-bridge.mp3'},
  {start: 110, file: 'audio/03-negative.mp3'},
  {start: 145, file: 'audio/04-authority.mp3'},
] as const;

const UI_REF = 'judge-uiux-opus-v0.1';
const uiShot = (name: string) =>
  `https://raw.githubusercontent.com/Faadil1/ERRATA/${UI_REF}/docs/ui/${name}`;

const liveClips = [
  {start: 24, duration: 43, file: 'live/01-base-voice.mp4', label: 'LIVE · BASE AMENDMENT · ASSEMBLYAI + AI33'},
  {start: 67, duration: 43, file: 'live/02-correction-en-fr.mp4', label: 'LIVE · SAME-IDENTITY CORRECTION · ASSEMBLYAI + AI33'},
  {start: 110, duration: 35, file: 'live/03-negative-ghost.mp4', label: 'LIVE · GHOST / ZERO EFFECT · AI33 GUIDANCE'},
  {start: 145, duration: 29, file: 'live/04-stale-current-commit.mp4', label: 'LIVE · HASH-BOUND COMMIT'},
] as const;

const FilmSection: React.FC<{title: string; kicker: string; children?: React.ReactNode}> = ({title, kicker, children}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const opacity = interpolate(frame, [0, Math.round(.35 * fps)], [0, 1], {extrapolateRight: 'clamp'});
  const y = interpolate(frame, [0, Math.round(.45 * fps)], [36, 0], {extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{
      background: palette.paper,
      color: palette.ink,
      fontFamily: 'Arial Narrow, Aptos Display, sans-serif',
      padding: 88,
      opacity,
    }}>
      <div style={{
        position: 'absolute',
        inset: 0,
        backgroundImage:
          'linear-gradient(rgba(22,24,20,.035) 1px, transparent 1px), linear-gradient(90deg, rgba(22,24,20,.035) 1px, transparent 1px)',
        backgroundSize: '64px 64px',
      }}/>
      <div style={{position: 'relative', transform: `translateY(${y}px)`}}>
        <div style={{fontFamily: 'Consolas, monospace', fontSize: 22, fontWeight: 800, letterSpacing: 3, color: palette.muted}}>
          {kicker}
        </div>
        <div style={{fontSize: 94, lineHeight: .96, letterSpacing: -5, fontWeight: 900, maxWidth: 1500, marginTop: 26}}>
          {title}
        </div>
        {children}
      </div>
      <div style={{position: 'absolute', right: 70, top: 48, fontFamily: 'Consolas, monospace', fontSize: 26, fontWeight: 900}}>ERRATA</div>
    </AbsoluteFill>
  );
};

const Placeholder: React.FC<{label: string; detail: string}> = ({label, detail}) => (
  <div style={{
    marginTop: 44,
    border: `2px solid ${palette.ink}`,
    padding: 34,
    background: 'rgba(255,255,255,.55)',
    boxShadow: '14px 14px 0 rgba(22,24,20,.08)',
    maxWidth: 1480,
  }}>
    <div style={{fontFamily: 'Consolas, monospace', fontSize: 18, letterSpacing: 2, color: palette.signal, fontWeight: 900}}>{label}</div>
    <div style={{fontFamily: 'Consolas, monospace', fontSize: 32, lineHeight: 1.35, marginTop: 18}}>{detail}</div>
  </div>
);

export const JudgeFilm: React.FC<JudgeFilmProps> = ({useNarration, useLiveFootage, useHyperframes, useBandwidthProof}) => {
  return (
    <AbsoluteFill style={{background: palette.paper}}>
      {segments.map((segment) => (
        <Sequence key={segment.id} from={sec(segment.start)} durationInFrames={sec(segment.duration)}>
          <FilmSection title={segment.title} kicker={segment.kicker}>
            {segment.id === 'hook' && (
              <Placeholder label="CORE INVARIANT" detail="same change_id · versioned repair · human Apply boundary" />
            )}
            {segment.id === 'problem' && (
              <Placeholder label="REAL USER" detail="Transit service controller · active disruption · hands already occupied" />
            )}
            {segment.id === 'live-core' && !useLiveFootage && (
              <Img src={uiShot('02-on-air-draft-not-on-air.png')} style={{marginTop: 36, width: '100%', maxHeight: 610, objectFit: 'contain', border: '2px solid #161814'}} />
            )}
            {segment.id === 'negative' && !useLiveFootage && (
              <Img src={uiShot('03-on-air-dropped-frame.png')} style={{marginTop: 36, width: '100%', maxHeight: 610, objectFit: 'contain', border: '2px solid #161814'}} />
            )}
            {segment.id === 'authority' && !useLiveFootage && (
              <Img src={uiShot('05-commit-stale-refused.png')} style={{marginTop: 36, width: '100%', maxHeight: 610, objectFit: 'contain', border: '2px solid #161814'}} />
            )}
            {segment.id === 'sponsor' && (
              <Placeholder label="ASSEMBLYAI" detail="Universal-3.5 Pro Realtime · EN/FR steering · keyterms · agent_context · deterministic downstream authority." />
            )}
            {segment.id === 'consequence' && (
              useLiveFootage
                ? <Placeholder label="DOWNSTREAM" detail="Serialized GTFS-RT protobuf → independent wire consumer → current truth visible outside the voice UI." />
                : <Img src={uiShot('07-feed-decoded-gtfs-rt.png')} style={{marginTop: 36, width: '100%', maxHeight: 610, objectFit: 'contain', border: '2px solid #161814'}} />
            )}
            {segment.id === 'business' && (
              <Placeholder label="WHY VOICE" detail="Hands-free operational control without making probabilistic speech the mutation authority." />
            )}
            {segment.id === 'truth' && (
              <Placeholder label="TRUTH BOUNDARY" detail={useBandwidthProof ? 'Browser core + separately proven Bandwidth phone transport.' : 'Browser core proven. Optional phone transport omitted unless separately proven.'} />
            )}
          </FilmSection>
        </Sequence>
      ))}

      {useLiveFootage && liveClips.map((clip) => (
        <Sequence key={clip.file} from={sec(clip.start)} durationInFrames={sec(clip.duration)}>
          <AbsoluteFill style={{background: '#111'}}>
            <OffthreadVideo
              src={staticFile(clip.file)}
              style={{width: '100%', height: '100%', objectFit: 'cover'}}
            />
            <div style={{
              position: 'absolute', left: 44, top: 38, padding: '12px 16px',
              background: 'rgba(242,239,231,.92)', color: palette.ink,
              fontFamily: 'Consolas, monospace', fontSize: 18, fontWeight: 900,
            }}>{clip.label}</div>
          </AbsoluteFill>
        </Sequence>
      ))}

      {useHyperframes && (
        <Sequence from={sec(174)} durationInFrames={sec(16)}>
          <AbsoluteFill style={{background: '#111'}}>
            <OffthreadVideo
              src={staticFile('hyperframes/architecture.mp4')}
              style={{width: '100%', height: '100%', objectFit: 'cover'}}
            />
          </AbsoluteFill>
        </Sequence>
      )}

      {useNarration && narration.map((track) => (
        <Sequence key={track.file} from={sec(track.start)}>
          <Audio src={staticFile(track.file)} />
        </Sequence>
      ))}
      {useNarration && !useLiveFootage && fallbackNarration.map((track) => (
        <Sequence key={track.file} from={sec(track.start)}>
          <Audio src={staticFile(track.file)} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
