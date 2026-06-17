// Admin-only bundle: the Trix rich-text editor. Loaded only by dashboard pages,
// so the public site stays lean. Editor output is HTML and is sanitized
// server-side with nh3 on save (apps/content), so this stays a pure UI concern.
import "trix";
import "trix/dist/trix.css";
import "./admin.css";
