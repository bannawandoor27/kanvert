import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { 
  Menu, 
  X, 
  FileText, 
  User, 
  Settings, 
  LogOut, 
  Bell,
  ChevronDown,
  Zap,
  BarChart3,
  Clock,
  LayoutDashboard,
  Home,
  DollarSign,
  Book
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '../common';
import { useAuthStore, useNotificationStore } from '../../stores';
import { NAVIGATION_LINKS } from '../../constants';
import { cn } from '../../utils';

const Header: React.FC = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  
  const { user, isAuthenticated, logout } = useAuthStore();
  const { notifications } = useNotificationStore();
  const unreadCount = notifications.filter(n => !n.read).length;
  
  const isActive = (href: string) => {
    if (href === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(href);
  };
  
  const handleLogout = () => {
    logout();
    navigate('/');
    setUserMenuOpen(false);
  };
  
  const navLinks = isAuthenticated ? NAVIGATION_LINKS.AUTHENTICATED : NAVIGATION_LINKS.PUBLIC;
  
  return (
    <header className="sticky top-0 z-50 bg-white/95 backdrop-blur-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link 
            to="/" 
            className="flex items-center space-x-2 text-brand-600 font-bold text-xl hover:text-brand-700 transition-colors"
          >
            <div className="p-2 bg-brand-100 rounded-lg">
              <FileText className="h-6 w-6" />
            </div>
            <span className="gradient-text">Kanvert</span>
          </Link>
          
          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-1">
            {navLinks.map((link) => {
              const iconMap = {
                Home: Home,
                Zap: Zap,
                DollarSign: DollarSign,
                Book: Book,
                LayoutDashboard: LayoutDashboard,
                FileText: FileText,
                Clock: Clock,
                BarChart3: BarChart3,
                Settings: Settings,
              };
              
              const IconComponent = iconMap[link.icon as keyof typeof iconMap] || FileText;
              
              return (
                <Link
                  key={link.href}
                  to={link.href}
                  className={cn(
                    'flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200',
                    isActive(link.href)
                      ? 'text-brand-600 bg-brand-50'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                  )}
                >
                  <IconComponent className="h-4 w-4" />
                  <span>{link.name}</span>
                </Link>
              );
            })}
          </nav>
          
          {/* Right side actions */}
          <div className="flex items-center space-x-4">
            {isAuthenticated ? (
              <>
                {/* Notifications */}
                <div className="relative">
                  <Button
                    variant="ghost"
                    size="sm"
                    className="relative p-2"
                    onClick={() => navigate('/notifications')}
                  >
                    <Bell className="h-5 w-5" />
                    {unreadCount > 0 && (
                      <span className="absolute -top-1 -right-1 h-5 w-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
                        {unreadCount > 9 ? '9+' : unreadCount}
                      </span>
                    )}
                  </Button>
                </div>
                
                {/* User Menu */}
                <div className="relative">
                  <Button
                    variant="ghost"
                    size="sm"
                    className="flex items-center space-x-2 p-2"
                    onClick={() => setUserMenuOpen(!userMenuOpen)}
                  >
                    <div className="h-8 w-8 bg-brand-100 rounded-full flex items-center justify-center">
                      <User className="h-4 w-4 text-brand-600" />
                    </div>
                    <span className="hidden sm:block text-sm font-medium text-gray-700">
                      {user?.name || user?.email}
                    </span>
                    <ChevronDown className={cn(
                      'h-4 w-4 text-gray-400 transition-transform duration-200',
                      userMenuOpen && 'rotate-180'
                    )} />
                  </Button>
                  
                  <AnimatePresence>
                    {userMenuOpen && (
                      <motion.div
                        initial={{ opacity: 0, scale: 0.95, y: -10 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95, y: -10 }}
                        transition={{ duration: 0.2 }}
                        className="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-strong border border-gray-200 py-1 z-50"
                      >
                        <div className="px-4 py-2 border-b border-gray-100">
                          <p className="text-sm font-medium text-gray-900">{user?.name}</p>
                          <p className="text-xs text-gray-500">{user?.email}</p>
                          <p className="text-xs text-brand-600 mt-1 capitalize">
                            {user?.subscription.toLowerCase()} Plan
                          </p>
                        </div>
                        
                        <Link
                          to="/settings"
                          className="flex items-center space-x-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                          onClick={() => setUserMenuOpen(false)}
                        >
                          <Settings className="h-4 w-4" />
                          <span>Settings</span>
                        </Link>
                        
                        <Link
                          to="/dashboard"
                          className="flex items-center space-x-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                          onClick={() => setUserMenuOpen(false)}
                        >
                          <Zap className="h-4 w-4" />
                          <span>Dashboard</span>
                        </Link>
                        
                        <hr className="my-1" />
                        
                        <button
                          onClick={handleLogout}
                          className="flex items-center space-x-2 w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors"
                        >
                          <LogOut className="h-4 w-4" />
                          <span>Sign out</span>
                        </button>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              </>
            ) : (
              <div className="flex items-center space-x-3">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => navigate('/login')}
                >
                  Sign in
                </Button>
                <Button
                  variant="primary"
                  size="sm"
                  onClick={() => navigate('/register')}
                >
                  Get started
                </Button>
              </div>
            )}
            
            {/* Mobile menu button */}
            <Button
              variant="ghost"
              size="sm"
              className="md:hidden p-2"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </Button>
          </div>
        </div>
        
        {/* Mobile Navigation */}
        <AnimatePresence>
          {mobileMenuOpen && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.2 }}
              className="md:hidden border-t border-gray-200 py-4"
            >
              <nav className="flex flex-col space-y-2">
                {navLinks.map((link) => {
                  const iconMap = {
                    Home: Home,
                    Zap: Zap,
                    DollarSign: DollarSign,
                    Book: Book,
                    LayoutDashboard: LayoutDashboard,
                    FileText: FileText,
                    Clock: Clock,
                    BarChart3: BarChart3,
                    Settings: Settings,
                  };
                  
                  const IconComponent = iconMap[link.icon as keyof typeof iconMap] || FileText;
                  
                  return (
                    <Link
                      key={link.href}
                      to={link.href}
                      className={cn(
                        'flex items-center space-x-3 px-3 py-2 rounded-lg text-base font-medium transition-colors',
                        isActive(link.href)
                          ? 'text-brand-600 bg-brand-50'
                          : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                      )}
                      onClick={() => setMobileMenuOpen(false)}
                    >
                      <IconComponent className="h-5 w-5" />
                      <span>{link.name}</span>
                    </Link>
                  );
                })}
                
                {!isAuthenticated && (
                  <div className="pt-4 border-t border-gray-200 space-y-2">
                    <Button
                      variant="outline"
                      className="w-full justify-center"
                      onClick={() => {
                        navigate('/login');
                        setMobileMenuOpen(false);
                      }}
                    >
                      Sign in
                    </Button>
                    <Button
                      variant="primary"
                      className="w-full justify-center"
                      onClick={() => {
                        navigate('/register');
                        setMobileMenuOpen(false);
                      }}
                    >
                      Get started
                    </Button>
                  </div>
                )}
              </nav>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </header>
  );
};

export default Header;
