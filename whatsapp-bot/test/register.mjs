// Lets Node import knowledge.md as text, the same way Cloudflare does.
import { register } from "node:module";
register("./md-loader.mjs", import.meta.url);
