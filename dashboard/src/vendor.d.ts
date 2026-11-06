/**
 * Ambient module declarations for dependencies that ship no bundled types.
 * These make the named imports `any` rather than erroring with TS7016 under
 * `strict`/`noImplicitAny`. globe.gl is intentionally NOT declared here - it
 * bundles its own `dist/globe.gl.d.ts`.
 */
declare module "topojson-client";
declare module "d3-geo";
