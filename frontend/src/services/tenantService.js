import api from "./api";

const registerTenant = async (datos) => {
    // POST /api/tenants/register/
    const response = await api.post('/tenants/register/', datos);
    return response.data;
};

export default {
    registerTenant
};