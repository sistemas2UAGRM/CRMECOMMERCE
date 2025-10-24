import { useState, useEffect } from 'react';
import { User, Mail, Lock, Save, ArrowLeft, Eye, EyeOff, CheckCircle, AlertCircle } from 'lucide-react';
import api from '../services/api';
import { clearAuthTokens } from '../utils/auth';


const UserProfile = ({ onBack }) => {
    // Estados principales
    const [profileData, setProfileData] = useState({
        id: '',
        username: '',
        email: '',
        first_name: '',
        last_name: '',
        is_active: true,
        date_joined: '',
        last_login: ''
    });

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [saving, setSaving] = useState(false);

    // Estados del formulario
    const [isEditing, setIsEditing] = useState(false);
    const [editedData, setEditedData] = useState({});

    // Estados del cambio de contraseña
    const [showPasswordForm, setShowPasswordForm] = useState(false);
    const [passwordData, setPasswordData] = useState({
        current_password: '',
        new_password: '',
        new_password_confirm: ''
    });
    const [showPasswords, setShowPasswords] = useState({
        current: false,
        new: false,
        confirm: false
    });
    const [passwordErrors, setPasswordErrors] = useState({});

    // Cargar datos del perfil
    useEffect(() => {
        fetchProfile();
    }, []);

    const fetchProfile = async () => {
        try {
            setLoading(true);
            const response = await api.get('/users/users/profile/');
            const data = response.data;
            setProfileData(data);
            setEditedData(data);
            setError('');
        } catch (err) {
            console.error('Error fetching profile:', err);
            if (err.response?.status === 401) {
                setError('Sesión expirada. Por favor, inicie sesión nuevamente.');
                clearAuthTokens();
            } else {
                const msg =
                    err.response?.data?.detail ||
                    err.response?.data?.message ||
                    'Error al cargar el perfil';
                setError(msg);
            }
        } finally {
            setLoading(false);
        }
    };

    // Guardar cambios del perfil
    const handleSaveProfile = async () => {
        try {
            setSaving(true);
            setError('');
            setSuccess('');

            const response = await api.put('/users/users/profile/', editedData);

            const data = response.data;
            setProfileData(data);
            setEditedData(data);
            setIsEditing(false);
            setSuccess('Perfil actualizado exitosamente');

            // Limpiar mensaje después de 3 segundos
            setTimeout(() => setSuccess(''), 3000);
        } catch (err) {
            console.error('Error saving profile:', err);
            if (err.response?.status === 401) {
                setError('Sesión expirada. Por favor, inicie sesión nuevamente.');
                clearAuthTokens();
            } else {
                const msg =
                    err.response?.data?.detail ||
                    JSON.stringify(err.response?.data) ||
                    'Error al actualizar el perfil';
                setError(msg);
            }
        } finally {
            setSaving(false);
        }
    };

    // Cambiar contraseña
    const handleChangePassword = async () => {
        try {
            setSaving(true);
            setPasswordErrors({});
            setError('');
            setSuccess('');

            // Validaciones básicas
            if (!passwordData.current_password || !passwordData.new_password || !passwordData.new_password_confirm) {
                setPasswordErrors({ general: 'Todos los campos son requeridos' });
                setSaving(false);
                return;
            }

            if (passwordData.new_password !== passwordData.new_password_confirm) {
                setPasswordErrors({ confirm: 'Las contraseñas nuevas no coinciden' });
                setSaving(false);
                return;
            }

            if (passwordData.new_password.length < 8) {
                setPasswordErrors({ new: 'La nueva contraseña debe tener al menos 8 caracteres' });
                setSaving(false);
                return;
            }

            await api.post('/users/users/profile/change-password/', passwordData);

            // Limpiar formulario y mostrar éxito
            setPasswordData({
                current_password: '',
                new_password: '',
                new_password_confirm: ''
            });
            setShowPasswordForm(false);
            setSuccess('Contraseña cambiada exitosamente');

            // Limpiar mensaje después de 3 segundos
            setTimeout(() => setSuccess(''), 3000);
        } catch (err) {
            console.error('Error changing password:', err);
            const errors = err.response?.data;
            if (errors) {
                const newErrors = {};
                for (const key in errors) {
                    if (Array.isArray(errors[key])) {
                        // Para errores como 'new_password' o 'current_password'
                        newErrors[key] = errors[key].join(' ');
                    }
                }
                if (errors.detail) newErrors.general = errors.detail;
                if (errors.error) newErrors.general = errors.error;
                if (Object.keys(newErrors).length === 0) {
                    newErrors.general = 'Error al cambiar la contraseña.';
                }
                setPasswordErrors(newErrors);
            } else {
                setPasswordErrors({ general: 'Error al cambiar la contraseña.' });
            }
        } finally {
            setSaving(false);
        }
    };

    // Manejar cambios en el formulario
    const handleInputChange = (field, value) => {
        setEditedData(prev => ({
            ...prev,
            [field]: value
        }));
    };

    // Manejar cambios en la contraseña
    const handlePasswordChange = (field, value) => {
        setPasswordData(prev => ({
            ...prev,
            [field]: value
        }));
        // Limpiar errores cuando el usuario empiece a escribir
        if (passwordErrors[field]) {
            setPasswordErrors(prev => ({
                ...prev,
                [field]: ''
            }));
        }
    };

    // Formatear fecha
    const formatDate = (dateString) => {
        if (!dateString) return 'Nunca';
        return new Date(dateString).toLocaleString('es-ES', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    if (loading) {
        return (
            <div className="p-6 bg-gray-50 min-h-screen">
                <div className="max-w-2xl mx-auto bg-white rounded-lg shadow-sm p-8 text-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
                    <p className="text-gray-600">Cargando perfil de usuario...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="p-6 bg-gray-50 min-h-screen">
            {/* Header con botón de regreso */}
            <div className="max-w-2xl mx-auto mb-6">
                <div className="flex items-center gap-4 mb-4">
                    <button
                        onClick={onBack}
                        className="flex items-center gap-2 text-gray-600 hover:text-gray-800 transition-colors"
                    >
                        <ArrowLeft className="w-5 h-5" />
                        Volver al Dashboard
                    </button>
                </div>
                <h1 className="text-2xl font-bold text-gray-800 mb-2">Mi Perfil</h1>
                <p className="text-gray-600">Gestiona tu información personal y configuración</p>
            </div>

            {/* Mensajes de estado */}
            {error && (
                <div className="max-w-2xl mx-auto mb-6">
                    <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center gap-3">
                        <AlertCircle className="w-5 h-5 text-red-500" />
                        <p className="text-red-800">{error}</p>
                    </div>
                </div>
            )}

            {success && (
                <div className="max-w-2xl mx-auto mb-6">
                    <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-center gap-3">
                        <CheckCircle className="w-5 h-5 text-green-500" />
                        <p className="text-green-800">{success}</p>
                    </div>
                </div>
            )}

            {/* Formulario de perfil */}
            <div className="max-w-2xl mx-auto bg-white rounded-lg shadow-sm overflow-hidden">
                {/* Avatar y información básica */}
                <div className="bg-gradient-to-r from-blue-600 to-blue-800 px-6 py-8 text-white text-center">
                    <div className="w-24 h-24 bg-white/20 rounded-full flex items-center justify-center mx-auto mb-4">
                        <User className="w-12 h-12" />
                    </div>
                    <h2 className="text-xl font-semibold mb-1">
                        {profileData.first_name} {profileData.last_name}
                    </h2>
                    <p className="text-blue-100">@{profileData.username}</p>
                    <div className="mt-4 flex justify-center gap-4 text-sm">
                        <div className="text-center">
                            <div className="font-medium">Miembro desde</div>
                            <div className="text-blue-100">{formatDate(profileData.date_joined).split(',')[0]}</div>
                        </div>
                        <div className="text-center">
                            <div className="font-medium">Último login</div>
                            <div className="text-blue-100">{formatDate(profileData.last_login)}</div>
                        </div>
                    </div>
                </div>

                {/* Información detallada */}
                <div className="p-6">
                    <div className="flex justify-between items-center mb-6">
                        <h3 className="text-lg font-semibold text-gray-800">Información Personal</h3>
                        <div className="flex gap-2">
                            {isEditing ? (
                                <>
                                    <button
                                        onClick={() => {
                                            setIsEditing(false);
                                            setEditedData(profileData);
                                        }}
                                        className="px-4 py-2 text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                                    >
                                        Cancelar
                                    </button>
                                    <button
                                        onClick={handleSaveProfile}
                                        disabled={saving}
                                        className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
                                    >
                                        {saving ? (
                                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                                        ) : (
                                            <Save className="w-4 h-4" />
                                        )}
                                        {saving ? 'Guardando...' : 'Guardar'}
                                    </button>
                                </>
                            ) : (
                                <button
                                    onClick={() => setIsEditing(true)}
                                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                                >
                                    Editar Perfil
                                </button>
                            )}
                        </div>
                    </div>

                    <div className="space-y-4">
                        {/* Nombre de usuario */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Nombre de Usuario
                            </label>
                            <div className="relative">
                                <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                                <input
                                    type="text"
                                    value={isEditing ? editedData.username : profileData.username}
                                    onChange={(e) => handleInputChange('username', e.target.value)}
                                    disabled={!isEditing}
                                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-50 disabled:text-gray-500"
                                />
                            </div>
                        </div>

                        {/* Email */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Correo Electrónico
                            </label>
                            <div className="relative">
                                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                                <input
                                    type="email"
                                    value={isEditing ? editedData.email : profileData.email}
                                    onChange={(e) => handleInputChange('email', e.target.value)}
                                    disabled={!isEditing}
                                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-50 disabled:text-gray-500"
                                />
                            </div>
                        </div>

                        {/* Nombres */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Nombre
                                </label>
                                <input
                                    type="text"
                                    value={isEditing ? editedData.first_name : profileData.first_name}
                                    onChange={(e) => handleInputChange('first_name', e.target.value)}
                                    disabled={!isEditing}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-50 disabled:text-gray-500"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Apellido
                                </label>
                                <input
                                    type="text"
                                    value={isEditing ? editedData.last_name : profileData.last_name}
                                    onChange={(e) => handleInputChange('last_name', e.target.value)}
                                    disabled={!isEditing}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-50 disabled:text-gray-500"
                                />
                            </div>
                        </div>
                    </div>

                    {/* Sección de cambio de contraseña */}
                    <div className="mt-8 pt-6 border-t border-gray-200">
                        <div className="flex justify-between items-center mb-4">
                            <h3 className="text-lg font-semibold text-gray-800">Seguridad</h3>
                            <button
                                onClick={() => setShowPasswordForm(!showPasswordForm)}
                                className="flex items-center gap-2 px-4 py-2 text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors"
                            >
                                <Lock className="w-4 h-4" />
                                Cambiar Contraseña
                            </button>
                        </div>

                        {showPasswordForm && (
                            <div className="bg-gray-50 p-4 rounded-lg space-y-4">
                                <h4 className="font-medium text-gray-800 mb-3">Cambiar Contraseña</h4>

                                {passwordErrors.general && (
                                    <div className="text-red-600 text-sm bg-red-50 p-3 rounded-lg">
                                        {passwordErrors.general}
                                    </div>
                                )}

                                {/* Contraseña actual */}
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Contraseña Actual
                                    </label>
                                    <div className="relative">
                                        <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                                        <input
                                            type={showPasswords.current ? 'text' : 'password'}
                                            value={passwordData.current_password}
                                            onChange={(e) => handlePasswordChange('current_password', e.target.value)}
                                            className="w-full pl-10 pr-12 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                            placeholder="Ingrese su contraseña actual"
                                        />
                                        <button
                                            type="button"
                                            onClick={() => setShowPasswords(prev => ({ ...prev, current: !prev.current }))}
                                            className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                                        >
                                            {showPasswords.current ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                                        </button>
                                    </div>
                                </div>

                                {/* Nueva contraseña */}
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Nueva Contraseña
                                    </label>
                                    <div className="relative">
                                        <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                                        <input
                                            type={showPasswords.new ? 'text' : 'password'}
                                            value={passwordData.new_password}
                                            onChange={(e) => handlePasswordChange('new_password', e.target.value)}
                                            className="w-full pl-10 pr-12 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                            placeholder="Ingrese la nueva contraseña"
                                        />
                                        <button
                                            type="button"
                                            onClick={() => setShowPasswords(prev => ({ ...prev, new: !prev.new }))}
                                            className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                                        >
                                            {showPasswords.new ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                                        </button>
                                    </div>
                                    {passwordErrors.new && (
                                        <p className="text-red-600 text-xs mt-1">{passwordErrors.new}</p>
                                    )}
                                </div>

                                {/* Confirmar nueva contraseña */}
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Confirmar Nueva Contraseña
                                    </label>
                                    <div className="relative">
                                        <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                                        <input
                                            type={showPasswords.confirm ? 'text' : 'password'}
                                            value={passwordData.new_password_confirm}
                                            onChange={(e) => handlePasswordChange('new_password_confirm', e.target.value)}
                                            className="w-full pl-10 pr-12 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                            placeholder="Confirme la nueva contraseña"
                                        />
                                        <button
                                            type="button"
                                            onClick={() => setShowPasswords(prev => ({ ...prev, confirm: !prev.confirm }))}
                                            className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                                        >
                                            {showPasswords.confirm ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                                        </button>
                                    </div>
                                    {passwordErrors.confirm && (
                                        <p className="text-red-600 text-xs mt-1">{passwordErrors.confirm}</p>
                                    )}
                                </div>

                                {/* Botones de acción para contraseña */}
                                <div className="flex gap-2 pt-2">
                                    <button
                                        onClick={() => {
                                            setShowPasswordForm(false);
                                            setPasswordData({
                                                current_password: '',
                                                new_password: '',
                                                new_password_confirm: ''
                                            });
                                            setPasswordErrors({});
                                        }}
                                        className="px-4 py-2 text-gray-600 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                                    >
                                        Cancelar
                                    </button>
                                    <button
                                        onClick={handleChangePassword}
                                        disabled={saving}
                                        className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50"
                                    >
                                        {saving ? (
                                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                                        ) : (
                                            <Save className="w-4 h-4" />
                                        )}
                                        {saving ? 'Cambiando...' : 'Cambiar Contraseña'}
                                    </button>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default UserProfile;