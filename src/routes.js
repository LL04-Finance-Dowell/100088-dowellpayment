import React from "react";
import { Routes, Route } from "react-router-dom";
import HOME from './components/Home';

const Pages = () => {
  return (
    <Routes>
      <Route path="/" element={<HOME />} />
    </Routes>
  );
};

export default Pages;