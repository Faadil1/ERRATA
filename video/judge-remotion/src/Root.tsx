import React from 'react';
import {Composition} from 'remotion';
import {JudgeFilm, judgeFilmSchemaDefaults} from './JudgeFilm';

export const Root: React.FC = () => {
  return (
    <Composition
      id="ERRATA-Judge"
      component={JudgeFilm}
      durationInFrames={280 * 30}
      fps={30}
      width={1920}
      height={1080}
      defaultProps={judgeFilmSchemaDefaults}
    />
  );
};
