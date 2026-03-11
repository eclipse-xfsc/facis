# DCM Platform

A flow-based backend application for the **DCM (Decentralised Catalogue Management)** platform, built on **ORCE** with a Vue 3 frontend.

---

## Repository Structure

```
backend/
  src/
    DCM-Configuration.json    # General configuration flow
    DCM-Login.json             # Authentication and session management flow
    DCM-Requests.json          # Password reset and verification flow
    DCM-Dashboards.json        # Dashboard operations and catalog management flow
    flows.json                 # Combined ORCE flow (all modules merged)

public/                        # Static assets served to the client
src/                           # Vue 3 frontend application source
```

---

## ORCE Flows

The backend logic is implemented as modular ORCE flows stored as JSON files in `backend/src/`:

| Flow | Purpose |
|------|---------|
| **DCM-Configuration** | AI prompt integration and general settings |
| **DCM-Login** | User authentication, token validation, and session handling |
| **DCM-Requests** | Password reset workflows including email verification codes |
| **DCM-Dashboards** | Dashboard access, catalog registry, user invitations, and admin tools |

`flows.json` is the combined flow file containing all modules, ready for import into a ORCE instance.

---

## Deployment

1. Start a ORCE instance
2. Import `backend/src/flows.json` via **Menu > Import**
3. Configure the MongoDB connection node with your credentials
4. Click **Deploy**

The frontend is served via the uibuilder node configured within the flows.
