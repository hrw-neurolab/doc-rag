const AUTH_BASE_URL = "/auth";
const authRoutes = {
  post: {
    register: () => `${AUTH_BASE_URL}/register`,
    login: () => `${AUTH_BASE_URL}/login`,
  },
  get: {
    refresh: () => `${AUTH_BASE_URL}/refresh`,
  },
};

const USERS_BASE_URL = "/users";
const usersRoutes = {
  get: {
    getUser: () => USERS_BASE_URL,
  },
  patch: {
    updateUser: () => USERS_BASE_URL,
  },
  delete: {
    deleteUser: () => USERS_BASE_URL,
  },
};

const RESOURCES_BASE_URL = "/resources";
const resourcesRoutes = {
  get: {
    getResources: () => RESOURCES_BASE_URL,
    getResource: (id: string) => `${RESOURCES_BASE_URL}/${id}`,
    getChunk: (id: string) => `${RESOURCES_BASE_URL}/chunk/${id}`,
  },
  post: {
    createPdfResource: () => `${RESOURCES_BASE_URL}/pdf`,
  },
  delete: {
    deleteResource: (id: string) => `${RESOURCES_BASE_URL}/${id}`,
  },
};

const CHAT_BASE_URL = "/chat";
const chatRoutes = {
  post: {
    sendMessage: () => `${CHAT_BASE_URL}`,
    clear: () => `${CHAT_BASE_URL}/clear`,
  },
};

export default {
  auth: authRoutes,
  users: usersRoutes,
  resources: resourcesRoutes,
  chat: chatRoutes,
};
