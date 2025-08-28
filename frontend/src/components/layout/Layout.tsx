import React from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import Header from './Header';
import Footer from './Footer';
import { ToastContainer } from '../common';
import { cn } from '../../utils';

interface LayoutProps {
  children?: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const location = useLocation();
  
  // Pages that should not show the footer
  const noFooterPages = ['/login', '/register', '/dashboard', '/convert', '/settings'];
  const shouldShowFooter = !noFooterPages.some(page => location.pathname.startsWith(page));
  
  // Pages that should have full height
  const fullHeightPages = ['/dashboard', '/convert', '/analytics'];
  const isFullHeight = fullHeightPages.some(page => location.pathname.startsWith(page));
  
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Header />
      
      <main 
        className={cn(
          'flex-1',
          isFullHeight ? 'h-full' : 'min-h-0'
        )}
      >
        {children || <Outlet />}
      </main>
      
      {shouldShowFooter && <Footer />}
      
      {/* Toast notifications */}
      <ToastContainer />
    </div>
  );
};

export default Layout;