/**
 * FACIS service adapter
 * - Uses real window.uibuilder when available (Node-RED)
 * - Falls back to a mock that prevents errors and feeds sample data (FACIS Preview)
 */

const mockUsers = [
  {
    uniqueId: "u1",
    profile: { firstName: "Alice", lastName: "Schmidt" },
    email: "alice@example.com",
    status: "Active",
    access: ["local_catalogue", "catalogue_registry", "schema_registry", "admin_tools", "harvester"]
  },
  {
    uniqueId: "u2",
    profile: { firstName: "Bob", lastName: "Mueller" },
    email: "bob@example.com",
    status: "Active",
    access: ["local_catalogue", "catalogue_registry"]
  },
  {
    uniqueId: "u3",
    profile: { firstName: "Clara", lastName: "Fischer" },
    email: "clara@example.com",
    status: "Invited",
    access: ["local_catalogue", "schema_registry", "harvester"]
  }
];

const mockCatalogs = [
  {
    uniqueId: "rc1",
    catalog: {
      catalogId: "rc1",
      catalogName: "SensorML Europe",
      owner: "EU Sensors Consortium",
      strategy: "deterministic",
      baseEndpoint: "https://api.sensorml-eu.org/sparql",
      enabled: true
    }
  },
  {
    uniqueId: "rc2",
    catalog: {
      catalogId: "rc2",
      catalogName: "DCAT-AP Germany",
      owner: "GovData.de",
      strategy: "ai",
      baseEndpoint: "https://govdata.de/ckan/api",
      enabled: true
    }
  },
  {
    uniqueId: "rc3",
    catalog: {
      catalogId: "rc3",
      catalogName: "OGC Observations",
      owner: "OGC Foundation",
      strategy: "hybrid",
      baseEndpoint: "https://ogc.org/api/observations",
      enabled: false
    }
  }
];

let msgCallbacks = [];
let _isMock = false;

function dispatchMsg(msg) {
  setTimeout(() => {
    msgCallbacks.forEach((cb) => {
      try { cb(msg); }
      catch (e) { console.error("[facis-service] callback error:", e); }
    });
  }, 150);
}

function createMockResponder(msg) {
  if (!msg) return;

  if (msg.type === "getDashboard") {
    dispatchMsg({
      payload: {
        type: "getDashboard",
        response: {
          action: "getDashboard",
          status: "success",
          userAccess: ["local_catalogue", "catalogue_registry", "schema_registry", "admin_tools", "harvester"],
          userPermissions: {
            local_catalogue:    { read: true, create: false, update: false, delete: false },
            catalogue_registry: { read: true, create: true, update: true, delete: true },
            schema_registry:    { read: true, create: true, update: true, delete: true },
            harvester:          { read: true, create: true, update: true, delete: false },
            admin_tools:        { read: true, create: true, update: true, delete: true },
          }
        }
      }
    });
  }

  if (msg.type === "getCatalogRegistry") {
    dispatchMsg({
      payload: {
        response: {
          action: "getCatalogRegistry",
          status: "success",
          catalogs: mockCatalogs
        }
      }
    });
  }

  if (msg.type === "getAdminTools") {
    dispatchMsg({
      type: "getAdminTools",
      response: { status: "success", users: mockUsers }
    });
  }

  if (msg.type === "inviteUser") {
    dispatchMsg({
      payload: {
        data: msg.data,
        response: {
          action: "inviteUser",
          status: "success",
          uniqueId: "mock-" + Date.now()
        }
      }
    });
  }

  if (msg.type === "registerRemoteCatalog") {
    dispatchMsg({
      payload: {
        response: {
          action: "registerRemoteCatalog",
          status: "success",
          uniqueId: "mock-rc-" + Date.now()
        }
      }
    });
  }

  if (msg.type === "updateRemoteCatalog") {
    dispatchMsg({
      payload: {
        data: msg.data,
        response: {
          action: "updateRemoteCatalog",
          status: "success"
        }
      }
    });
  }

  if (msg.type === "logOut") {
    console.log("[facis-service] Logout requested (no redirect in preview)");
  }
}

const mockAdapter = {
  start() {
    console.log("[facis-service] mock start()");
  },
  send(msg) {
    console.log("[facis-service] mock send():", JSON.stringify(msg, null, 2));
    createMockResponder(msg);
  },
  onChange(prop, cb) {
    if (prop === "msg" && typeof cb === "function") {
      msgCallbacks.push(cb);
    }
  },
  get(prop) {
    if (prop === "clientId") return "mock-client-001";
    return undefined;
  },
  set() {},
  eventSend() {}
};

const uibuilderService = {
  init() {
    if (window.uibuilder) {
      _isMock = false;
      console.log("[facis-service] Using real uibuilder");
    } else {
      _isMock = true;
      window.uibuilder = mockAdapter;
      console.log("[facis-service] Mock uibuilder activated");
    }
  },

  onMessage(handler) {
    if (_isMock) {
      msgCallbacks.push(handler);
    } else {
      window.uibuilder.onChange("msg", handler);
    }
  },

  send(msg) {
    window.uibuilder.send(msg);
  },

  start() {
    window.uibuilder.start();
  },

  get(prop) {
    return window.uibuilder.get(prop);
  },

  isMock() {
    return _isMock;
  }
};

export { uibuilderService };
