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
                <TableCell style={{ fontWeight: "bold" }}>
                  Base Country
                </TableCell>
                <TableCell style={{ fontWeight: "bold" }}>
                  {results?.base_country}
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell style={{ fontWeight: "bold" }}>
                  Base Price In Germany
                </TableCell>
                <TableCell style={{ fontWeight: "bold" }}>
                  {results?.base_country}
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell style={{ fontWeight: "bold" }}>
                  Calculated Price In USA
                </TableCell>
                <TableCell style={{ fontWeight: "bold" }}>
                  {results?.calculated_price_base_on_ppp}
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell style={{ fontWeight: "bold" }}>
                  Price in base currency
                </TableCell>
                <TableCell style={{ fontWeight: "bold" }}>
                  {results?.price_in_base_country}
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell style={{ fontWeight: "bold" }}>
                  Target Country
                </TableCell>
                <TableCell style={{ fontWeight: "bold" }}>
                  {results?.target_country}
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell style={{ fontWeight: "bold" }}>
                  Target currency exchange rate
                </TableCell>
                <TableCell style={{ fontWeight: "bold" }}>
                  {results?.target_price}
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell style={{ fontWeight: "bold" }}>
                  Calculated Price based on purchasing power
                </TableCell>
                <TableCell style={{ fontWeight: "bold" }}>
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
