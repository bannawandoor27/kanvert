import React from 'react';
import { Hero, Features, Pricing } from '../components/sections';

const LandingPage: React.FC = () => {
  return (
    <div className="min-h-screen">
      <Hero />
      <Features />
      <Pricing />
    </div>
  );
};

export default LandingPage;