import React from "react";
import {
  TableContainer,
  Table,
  TableHead,
  TableRow,
  TableBody,
  TableCell,
} from "@mui/material";
import Paper from "@mui/material/Paper";

const ResultComponent = ({ results, error }) => {
  function toTitleCaseWithSpaces(str) {
    return str
      .split("_")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");
  }
  let fieldNameOne;
  let fieldValueOne;
  let fieldNameTwo;
  let fieldValueTwo;

  for (const key in results) {
    if (key.startsWith("base_price_in_")) {
      fieldNameOne = toTitleCaseWithSpaces(key);
      fieldValueOne = results[key];
      console.log(`Field Name: ${fieldNameOne}, Field Value: ${fieldValueOne}`);
    }
    if (key.startsWith("calculated_price_in")) {
      fieldNameTwo = toTitleCaseWithSpaces(key);
      fieldValueTwo = results[key];
      console.log(`Field Name: ${fieldNameTwo}, Field Value: ${fieldValueTwo}`);
    }
  }

  const resultContainerStyle = {
    border: "1px solid #ccc", // Add border style here
    borderRadius: "5px", // Add border radius here
    padding: "20px",
    marginLeft: "10px",
  };
  return (
    <div style={resultContainerStyle}>
      {error && <div style={{ color: "red", marginTop: "16px" }}>{error}</div>}
      <>
        <TableContainer component={Paper} variant="outlined">
          <Table>
            <TableHead>
              <TableRow>
                <TableCell style={{ fontWeight: "bold" }}>Items</TableCell>
                <TableCell style={{ fontWeight: "bold" }}>Value</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              <TableRow>
                <TableCell style={{ fontWeight: "normal" }}>
                  Base Country
                </TableCell>
                <TableCell style={{ fontWeight: "normal" }}>
                  {results?.base_country}
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell style={{ fontWeight: "bold" }}>
                  {fieldNameOne || "Base Price In Base Country"}
                </TableCell>
                <TableCell style={{ fontWeight: "bold" }}>
                  {fieldValueOne}
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell style={{ fontWeight: "bold" }}>
                  {fieldNameTwo || "Calculated Price in Target Country"}
                </TableCell>
                <TableCell style={{ fontWeight: "bold" }}>
                  {fieldValueTwo}
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell style={{ fontWeight: "normal" }}>
                  Price in base currency
                </TableCell>
                <TableCell style={{ fontWeight: "normal" }}>
                  {results?.price_in_base_country}
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell style={{ fontWeight: "normal" }}>
                  Target Country
                </TableCell>
                <TableCell style={{ fontWeight: "normal" }}>
                  {results?.target_country}
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell style={{ fontWeight: "normal" }}>
                  Target currency exchange rate
                </TableCell>
                <TableCell style={{ fontWeight: "normal" }}>
                  {results?.target_price}
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell style={{ fontWeight: "normal" }}>
                  Calculated Price based on purchasing power
                </TableCell>
                <TableCell style={{ fontWeight: "normal" }}>
                  {results?.calculated_price_base_on_ppp}
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </TableContainer>
      </>
    </div>
  );
};

export default ResultComponent;
