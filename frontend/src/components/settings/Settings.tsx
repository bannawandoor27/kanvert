import React, { useState } from 'react';
import {
  User,
  Key,
  Bell,
  Shield,
  CreditCard,
  Palette,
  Globe,
  Save,
  Eye,
  EyeOff,
  Copy,
  Trash2,
  Plus
} from 'lucide-react';
import { Button, Badge, Card, Input } from '../common';
import { useAuthStore } from '../../stores/authStore';
import { cn } from '../../utils';
import { toast } from 'react-hot-toast';

interface UserProfile {
  firstName: string;
  lastName: string;
  email: string;
  timezone: string;
  language: string;
  company?: string;
  jobTitle?: string;
}

interface ApiKey {
  id: string;
  name: string;
  key: string;
  createdAt: Date;
  lastUsed?: Date;
  permissions: string[];
}

interface NotificationSettings {
  emailNotifications: boolean;
  conversionComplete: boolean;
  conversionFailed: boolean;
  weeklyDigest: boolean;
  productUpdates: boolean;
  securityAlerts: boolean;
}

interface PreferenceSettings {
  theme: 'light' | 'dark' | 'system';
  language: string;
  timezone: string;
  defaultOutputFormat: string;
  autoDownload: boolean;
  retainFiles: number; // days
}

const Settings: React.FC = () => {
  const { user, updateUser } = useAuthStore();
  const [activeTab, setActiveTab] = useState('profile');
  const [showApiKey, setShowApiKey] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Profile State
  const [profile, setProfile] = useState<UserProfile>({
    firstName: user?.name?.split(' ')[0] || '',
    lastName: user?.name?.split(' ').slice(1).join(' ') || '',
    email: user?.email || '',
    timezone: 'America/New_York',
    language: 'en',
    company: '',
    jobTitle: ''
  });

  // API Keys State
  const [apiKeys] = useState<ApiKey[]>([
    {
      id: '1',
      name: 'Production Key',
      key: 'sk-1234567890abcdef1234567890abcdef',
      createdAt: new Date('2024-01-01'),
      lastUsed: new Date('2024-01-15'),
      permissions: ['convert', 'history']
    },
    {
      id: '2',
      name: 'Development Key',
      key: 'sk-abcdef1234567890abcdef1234567890',
      createdAt: new Date('2024-01-10'),
      permissions: ['convert']
    }
  ]);

  // Notifications State
  const [notifications, setNotifications] = useState<NotificationSettings>({
    emailNotifications: true,
    conversionComplete: true,
    conversionFailed: true,
    weeklyDigest: false,
    productUpdates: true,
    securityAlerts: true
  });

  // Preferences State
  const [preferences, setPreferences] = useState<PreferenceSettings>({
    theme: 'light',
    language: 'en',
    timezone: 'America/New_York',
    defaultOutputFormat: 'pdf',
    autoDownload: false,
    retainFiles: 30
  });

  const tabs = [
    { id: 'profile', name: 'Profile', icon: User },
    { id: 'apikeys', name: 'API Keys', icon: Key },
    { id: 'notifications', name: 'Notifications', icon: Bell },
    { id: 'preferences', name: 'Preferences', icon: Palette },
    { id: 'billing', name: 'Billing', icon: CreditCard },
    { id: 'security', name: 'Security', icon: Shield }
  ];

  const handleProfileSave = async () => {
    setIsLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const fullName = `${profile.firstName} ${profile.lastName}`.trim();
      updateUser({ name: fullName, email: profile.email });
      
      toast.success('Profile updated successfully');
    } catch {
      toast.error('Failed to update profile');
    } finally {
      setIsLoading(false);
    }
  };

  const handleNotificationChange = (key: keyof NotificationSettings, value: boolean) => {
    setNotifications(prev => ({ ...prev, [key]: value }));
  };

  const handlePreferenceChange = (key: keyof PreferenceSettings, value: string | number | boolean) => {
    setPreferences(prev => ({ ...prev, [key]: value }));
  };

  const copyApiKey = (key: string) => {
    navigator.clipboard.writeText(key);
    toast.success('API key copied to clipboard');
  };

  const generateNewApiKey = () => {
    toast.success('New API key generated');
  };

  const revokeApiKey = (_keyId: string) => {
    toast.success('API key revoked');
  };

  const maskApiKey = (key: string) => {
    if (showApiKey === key) return key;
    return key.slice(0, 8) + '•'.repeat(24) + key.slice(-4);
  };

  const renderProfileTab = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Personal Information</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              First Name
            </label>
            <Input
              value={profile.firstName}
              onChange={(e) => setProfile(prev => ({ ...prev, firstName: e.target.value }))}
              placeholder="Enter first name"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Last Name
            </label>
            <Input
              value={profile.lastName}
              onChange={(e) => setProfile(prev => ({ ...prev, lastName: e.target.value }))}
              placeholder="Enter last name"
            />
          </div>
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Email Address
            </label>
            <Input
              type="email"
              value={profile.email}
              onChange={(e) => setProfile(prev => ({ ...prev, email: e.target.value }))}
              placeholder="Enter email address"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Company (Optional)
            </label>
            <Input
              value={profile.company}
              onChange={(e) => setProfile(prev => ({ ...prev, company: e.target.value }))}
              placeholder="Enter company name"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Job Title (Optional)
            </label>
            <Input
              value={profile.jobTitle}
              onChange={(e) => setProfile(prev => ({ ...prev, jobTitle: e.target.value }))}
              placeholder="Enter job title"
            />
          </div>
        </div>
      </div>

      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Regional Settings</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Timezone
            </label>
            <select
              value={profile.timezone}
              onChange={(e) => setProfile(prev => ({ ...prev, timezone: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500"
            >
              <option value="America/New_York">Eastern Time (UTC-5)</option>
              <option value="America/Chicago">Central Time (UTC-6)</option>
              <option value="America/Denver">Mountain Time (UTC-7)</option>
              <option value="America/Los_Angeles">Pacific Time (UTC-8)</option>
              <option value="Europe/London">London (UTC+0)</option>
              <option value="Europe/Paris">Paris (UTC+1)</option>
              <option value="Asia/Tokyo">Tokyo (UTC+9)</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Language
            </label>
            <select
              value={profile.language}
              onChange={(e) => setProfile(prev => ({ ...prev, language: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500"
            >
              <option value="en">English</option>
              <option value="es">Español</option>
              <option value="fr">Français</option>
              <option value="de">Deutsch</option>
              <option value="ja">日本語</option>
            </select>
          </div>
        </div>
      </div>

      <div className="flex justify-end">
        <Button
          variant="primary"
          onClick={handleProfileSave}
          loading={isLoading}
          leftIcon={<Save className="h-4 w-4" />}
        >
          Save Changes
        </Button>
      </div>
    </div>
  );

  const renderApiKeysTab = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h3 className="text-lg font-medium text-gray-900">API Keys</h3>
          <p className="text-sm text-gray-600 mt-1">
            Manage your API keys for programmatic access to Kanvert
          </p>
        </div>
        <Button
          variant="primary"
          onClick={generateNewApiKey}
          leftIcon={<Plus className="h-4 w-4" />}
        >
          Generate New Key
        </Button>
      </div>

      <div className="space-y-4">
        {apiKeys.map((apiKey) => (
          <div key={apiKey.id} className="border border-gray-200 rounded-lg p-4">
            <div className="flex justify-between items-start mb-3">
              <div>
                <h4 className="font-medium text-gray-900">{apiKey.name}</h4>
                <p className="text-sm text-gray-600">
                  Created {apiKey.createdAt.toLocaleDateString()}
                  {apiKey.lastUsed && ` • Last used ${apiKey.lastUsed.toLocaleDateString()}`}
                </p>
              </div>
              <div className="flex space-x-2">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowApiKey(showApiKey === apiKey.key ? null : apiKey.key)}
                >
                  {showApiKey === apiKey.key ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => copyApiKey(apiKey.key)}
                >
                  <Copy className="h-4 w-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => revokeApiKey(apiKey.id)}
                  className="text-red-600 hover:text-red-700"
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </div>
            
            <div className="bg-gray-50 rounded p-3 font-mono text-sm">
              {maskApiKey(apiKey.key)}
            </div>
            
            <div className="flex flex-wrap gap-2 mt-3">
              {apiKey.permissions.map((permission) => (
                <Badge key={permission} variant="secondary">
                  {permission}
                </Badge>
              ))}
            </div>
          </div>
        ))}
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex">
          <Globe className="h-5 w-5 text-blue-600 mt-0.5" />
          <div className="ml-3">
            <h4 className="text-sm font-medium text-blue-800">API Documentation</h4>
            <p className="text-sm text-blue-700 mt-1">
              Learn how to integrate Kanvert API into your applications with our comprehensive documentation.
            </p>
            <Button variant="outline" size="sm" className="mt-3 border-blue-300 text-blue-700 hover:bg-blue-100">
              View Documentation
            </Button>
          </div>
        </div>
      </div>
    </div>
  );

  const renderNotificationsTab = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Email Notifications</h3>
        <div className="space-y-4">
          {Object.entries({
            emailNotifications: 'Enable email notifications',
            conversionComplete: 'Conversion completed',
            conversionFailed: 'Conversion failed',
            weeklyDigest: 'Weekly usage digest',
            productUpdates: 'Product updates and news',
            securityAlerts: 'Security alerts'
          }).map(([key, label]) => (
            <div key={key} className="flex items-center justify-between">
              <div>
                <p className="font-medium text-gray-900">{label}</p>
                {key === 'securityAlerts' && (
                  <p className="text-sm text-gray-600">Important security notifications (always enabled)</p>
                )}
              </div>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={notifications[key as keyof NotificationSettings]}
                  onChange={(e) => handleNotificationChange(key as keyof NotificationSettings, e.target.checked)}
                  disabled={key === 'securityAlerts'}
                  className="h-4 w-4 text-brand-600 focus:ring-brand-500 border-gray-300 rounded"
                />
              </label>
            </div>
          ))}
        </div>
      </div>

      <div className="flex justify-end">
        <Button variant="primary" leftIcon={<Save className="h-4 w-4" />}>
          Save Preferences
        </Button>
      </div>
    </div>
  );

  const renderPreferencesTab = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Appearance</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Theme
            </label>
            <select
              value={preferences.theme}
              onChange={(e) => handlePreferenceChange('theme', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500"
            >
              <option value="light">Light</option>
              <option value="dark">Dark</option>
              <option value="system">System</option>
            </select>
          </div>
        </div>
      </div>

      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Conversion Defaults</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Default Output Format
            </label>
            <select
              value={preferences.defaultOutputFormat}
              onChange={(e) => handlePreferenceChange('defaultOutputFormat', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500"
            >
              <option value="pdf">PDF</option>
              <option value="docx">Word Document</option>
              <option value="html">HTML</option>
            </select>
          </div>
          
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-gray-900">Auto-download converted files</p>
              <p className="text-sm text-gray-600">Automatically download files when conversion is complete</p>
            </div>
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={preferences.autoDownload}
                onChange={(e) => handlePreferenceChange('autoDownload', e.target.checked)}
                className="h-4 w-4 text-brand-600 focus:ring-brand-500 border-gray-300 rounded"
              />
            </label>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Retain files for (days)
            </label>
            <select
              value={preferences.retainFiles}
              onChange={(e) => handlePreferenceChange('retainFiles', parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500"
            >
              <option value={7}>7 days</option>
              <option value={14}>14 days</option>
              <option value={30}>30 days</option>
              <option value={90}>90 days</option>
            </select>
          </div>
        </div>
      </div>

      <div className="flex justify-end">
        <Button variant="primary" leftIcon={<Save className="h-4 w-4" />}>
          Save Preferences
        </Button>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
          <p className="text-gray-600 mt-1">
            Manage your account settings and preferences
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Sidebar Navigation */}
          <div className="lg:col-span-1">
            <nav className="space-y-1">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={cn(
                      'w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-colors',
                      activeTab === tab.id
                        ? 'bg-brand-100 text-brand-700 font-medium'
                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                    )}
                  >
                    <Icon className="h-5 w-5" />
                    <span>{tab.name}</span>
                  </button>
                );
              })}
            </nav>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3">
            <Card className="p-6">
              {activeTab === 'profile' && renderProfileTab()}
              {activeTab === 'apikeys' && renderApiKeysTab()}
              {activeTab === 'notifications' && renderNotificationsTab()}
              {activeTab === 'preferences' && renderPreferencesTab()}
              {activeTab === 'billing' && (
                <div className="text-center py-12">
                  <CreditCard className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">Billing & Subscription</h3>
                  <p className="text-gray-600 mb-6">
                    Manage your subscription and billing information
                  </p>
                  <Button variant="primary">Manage Billing</Button>
                </div>
              )}
              {activeTab === 'security' && (
                <div className="text-center py-12">
                  <Shield className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">Security Settings</h3>
                  <p className="text-gray-600 mb-6">
                    Configure two-factor authentication and security preferences
                  </p>
                  <Button variant="primary">Security Settings</Button>
                </div>
              )}
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;