import "./styles.css";
import { loadReportData } from "./data";
import { renderError, renderReport } from "./render";

const root = document.querySelector<HTMLElement>("#app");

if (!root) {
  throw new Error("missing #app root");
}

loadReportData()
  .then((payload) => renderReport(root, payload))
  .catch((error) => renderError(root, String(error)));
