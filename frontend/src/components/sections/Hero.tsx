import React from 'react';
import { motion } from 'framer-motion';
import { ArrowRight, FileText, Zap, Shield, Users } from 'lucide-react';
import { Button } from '../common';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../stores';

const Hero: React.FC = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuthStore();
  
  const stats = [
    { label: 'Documents Converted', value: '10M+', icon: FileText },
    { label: 'API Requests/Month', value: '50M+', icon: Zap },
    { label: 'Enterprise Customers', value: '500+', icon: Shield },
    { label: 'Active Developers', value: '25K+', icon: Users },
  ];
  
  return (
    <div className="relative overflow-hidden bg-gradient-to-br from-white via-brand-50/30 to-blue-50">
      {/* Background decoration */}
      <div className="absolute inset-0">
        <div className="absolute top-0 left-1/2 transform -translate-x-1/2 w-full h-full">
          <div className="relative w-full h-full">
            <div className="absolute top-20 left-1/4 w-72 h-72 bg-brand-200/20 rounded-full blur-3xl" />
            <div className="absolute top-40 right-1/4 w-96 h-96 bg-purple-200/20 rounded-full blur-3xl" />
            <div className="absolute bottom-20 left-1/3 w-80 h-80 bg-blue-200/20 rounded-full blur-3xl" />
          </div>
        </div>
      </div>
      
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="pt-20 pb-16 sm:pt-24 sm:pb-20 lg:pt-32 lg:pb-28">
          {/* Main hero content */}
          <div className="text-center">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
            >
              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 leading-tight">
                <span className="block">Transform Documents</span>
                <span className="block gradient-text">with Professional APIs</span>
              </h1>
              
              <p className="mt-6 text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
                Convert Markdown, HTML, DOCX, and Office documents to PDF with enterprise-grade reliability. 
                Our powerful API handles complex formatting while maintaining professional quality.
              </p>
            </motion.div>
            
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4"
            >
              <Button
                size="lg"
                onClick={() => navigate(isAuthenticated ? '/convert' : '/register')}
                className="px-8 py-3 text-base font-semibold"
                rightIcon={<ArrowRight className="h-5 w-5" />}
              >
                {isAuthenticated ? 'Start Converting' : 'Get Started Free'}
              </Button>
              
              <Button
                variant="outline"
                size="lg"
                onClick={() => navigate('/docs')}
                className="px-8 py-3 text-base font-semibold"
              >
                View API Docs
              </Button>
            </motion.div>
            
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.6, delay: 0.4 }}
              className="mt-4 text-sm text-gray-500"
            >
              No credit card required • 10 free conversions • 5MB file limit
            </motion.p>
          </div>
          
          {/* Demo showcase */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.3 }}
            className="mt-16 lg:mt-20"
          >
            <div className="relative">
              {/* Demo video or screenshot placeholder */}
              <div className="mx-auto max-w-4xl">
                <div className="relative rounded-2xl overflow-hidden shadow-2xl bg-white border border-gray-200">
                  <div className="bg-gray-50 px-4 py-3 border-b border-gray-200 flex items-center space-x-2">
                    <div className="flex space-x-2">
                      <div className="w-3 h-3 bg-red-400 rounded-full" />
                      <div className="w-3 h-3 bg-yellow-400 rounded-full" />
                      <div className="w-3 h-3 bg-green-400 rounded-full" />
                    </div>
                    <div className="flex-1 text-center">
                      <span className="text-sm text-gray-600">kanvert.com/convert</span>
                    </div>
                  </div>
                  
                  <div className="aspect-video bg-gradient-to-br from-gray-50 to-white p-8 flex items-center justify-center">
                    <div className="text-center">
                      <div className="inline-flex items-center justify-center w-20 h-20 bg-brand-100 rounded-2xl mb-4">
                        <FileText className="h-10 w-10 text-brand-600" />
                      </div>
                      <h3 className="text-xl font-semibold text-gray-900 mb-2">
                        Professional Document Conversion
                      </h3>
                      <p className="text-gray-600">
                        Upload your document and watch it transform into a beautiful PDF in seconds
                      </p>
                      
                      {/* Animated conversion flow */}
                      <div className="mt-8 flex items-center justify-center space-x-4">
                        <div className="flex flex-col items-center">
                          <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-2">
                            <FileText className="h-6 w-6 text-blue-600" />
                          </div>
                          <span className="text-xs text-gray-500">Markdown</span>
                        </div>
                        
                        <div className="flex items-center">
                          <ArrowRight className="h-5 w-5 text-gray-400 animate-pulse" />
                        </div>
                        
                        <div className="flex flex-col items-center">
                          <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-2">
                            <FileText className="h-6 w-6 text-green-600" />
                          </div>
                          <span className="text-xs text-gray-500">PDF</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Floating elements */}
              <div className="absolute -top-4 -left-4 w-24 h-24 bg-gradient-to-r from-brand-400 to-brand-600 rounded-2xl opacity-20 blur-xl" />
              <div className="absolute -bottom-4 -right-4 w-32 h-32 bg-gradient-to-r from-purple-400 to-pink-600 rounded-2xl opacity-20 blur-xl" />
            </div>
          </motion.div>
          
          {/* Stats section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.6 }}
            className="mt-16 lg:mt-20"
          >
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-8">
              {stats.map((stat, index) => {
                const Icon = stat.icon;
                return (
                  <motion.div
                    key={stat.label}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: 0.7 + index * 0.1 }}
                    className="text-center"
                  >
                    <div className="inline-flex items-center justify-center w-12 h-12 bg-white rounded-xl shadow-soft border border-gray-200 mb-3">
                      <Icon className="h-6 w-6 text-brand-600" />
                    </div>
                    <div className="text-2xl lg:text-3xl font-bold text-gray-900">
                      {stat.value}
                    </div>
                    <div className="text-sm text-gray-600 mt-1">
                      {stat.label}
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default Hero;