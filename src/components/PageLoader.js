import React from "react";
import CircularProgress from "@mui/material/CircularProgress";
import "./Loader.css"; 

const PageLoader = () => {
  return (
    <div className="page-loader-container">
      <div className="page-loader">
        <CircularProgress size={50} thickness={4} />
      </div>
    </div>
  );
};

export default PageLoader;
