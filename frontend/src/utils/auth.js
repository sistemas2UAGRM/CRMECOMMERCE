
export const getAuthToken = () => {
    let token = localStorage.getItem('token');


    if (!token) {
        const oldToken = localStorage.getItem('accessToken');
        if (oldToken) {
            localStorage.setItem('token', oldToken);
            localStorage.removeItem('accessToken'); // limpiar el viejo
            token = oldToken;
            console.log('Token migrado de accessToken a token');
        }
    }

    return token;
};

export const clearAuthTokens = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('accessToken'); // por si acaso queda alguno
    localStorage.removeItem('refreshToken');
};

export const setAuthToken = (token, refreshToken = null) => {
    localStorage.setItem('token', token);
    if (refreshToken) {
        localStorage.setItem('refreshToken', refreshToken);
    }

    // Limpiar tokens con nombres antiguos
    localStorage.removeItem('accessToken');
};

export const isTokenExpired = (error) => {
    return error.status === 401 ||
        error.message?.includes('401') ||
        error.message?.includes('Unauthorized') ||
        error.message?.includes('Token inválido') ||
        error.message?.includes('Token expirado');
};