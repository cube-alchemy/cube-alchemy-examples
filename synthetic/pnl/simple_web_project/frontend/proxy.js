// Minimal JS proxy that forwards method calls to FastAPI
// Usage:
//   const cube = await CubeProxy.new();
//   const data = await cube.query('PNL');

const API_BASE = (window.API_BASE || 'http://localhost:8000');

class CubeProxy {
  constructor(id) {
    this.id = id;
    return new Proxy(this, {
      get: (target, prop, receiver) => {
        if (prop in target) return Reflect.get(target, prop, receiver);
        // Return a function that calls backend
        return async (...args) => {
          const payload = {
            cube_id: target.id,
            method: String(prop),
            args: args,
          };
          const r = await fetch(`${API_BASE}/cube/call`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
          });
          const json = await r.json();
          if (!r.ok || json.status !== 'ok') {
            const message = json?.detail || json?.error || 'Unknown error';
            throw new Error(message);
          }
          return json.result;
        };
      }
    });
  }

  static async new() {
    const r = await fetch(`${API_BASE}/cube/new`, { method: 'POST' });
    if (!r.ok) throw new Error('Failed to create cube');
    const json = await r.json();
    return new CubeProxy(json.cube_id);
  }
}

window.CubeProxy = CubeProxy;
