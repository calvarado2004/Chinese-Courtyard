// Minimal GLB sanity check: header, chunks, JSON glTF 2.0 structure, material names.
import fs from 'node:fs';
const files = process.argv.slice(2);
let fail = 0;
for (const f of files) {
  const buf = fs.readFileSync(f);
  const magic = buf.readUInt32LE(0);
  const version = buf.readUInt32LE(4);
  const length = buf.readUInt32LE(8);
  if (magic !== 0x46546c67) { console.log(`${f}: BAD MAGIC`); fail++; continue; }
  if (version !== 2) { console.log(`${f}: BAD VERSION ${version}`); fail++; continue; }
  if (length !== buf.length) { console.log(`${f}: LENGTH MISMATCH ${length} vs ${buf.length}`); fail++; continue; }
  const chunkLen = buf.readUInt32LE(12);
  const chunkType = buf.readUInt32LE(16);
  if (chunkType !== 0x4e4f534a) { console.log(`${f}: NO JSON CHUNK`); fail++; continue; }
  const json = JSON.parse(buf.slice(20, 20 + chunkLen).toString('utf8'));
  const meshes = (json.meshes || []).length;
  const prims = (json.meshes || []).reduce((a, m) => a + m.primitives.length, 0);
  const mats = (json.materials || []).map(m => m.name).sort();
  const nodes = (json.nodes || []).length;
  const scenes = (json.scenes || []).length;
  // verify accessors referenced by POSITION exist
  let badAcc = 0;
  for (const m of json.meshes || []) {
    for (const p of m.primitives) {
      const pos = p.attributes.POSITION;
      if (pos === undefined || !json.accessors[pos]) badAcc++;
    }
  }
  console.log(`${f}: OK scenes=${scenes} nodes=${nodes} meshes=${meshes} prims=${prims} mats=${mats.length} badAccessors=${badAcc}`);
  console.log(`  materials: ${mats.join(', ')}`);
  if (badAcc) fail++;
}
process.exit(fail ? 1 : 0);
