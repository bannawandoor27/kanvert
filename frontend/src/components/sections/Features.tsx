import React from 'react';
import { motion } from 'framer-motion';
import { 
  FileText, 
  Globe, 
  BarChart3, 
  GitCompare,
  Zap,
  Shield,
  Code,
  Clock,
  CheckCircle
} from 'lucide-react';
import { Card, CardContent } from '../common';
import { CONVERSION_FORMATS } from '../../constants';

const Features: React.FC = () => {
  const mainFeatures = [
    {
      icon: FileText,
      title: 'Multiple Format Support',
      description: 'Convert Markdown, HTML, DOCX, Excel, PowerPoint, and more to professional PDFs with preserved formatting.',
      highlights: ['Markdown to PDF', 'HTML to PDF', 'DOCX to PDF', 'Office to PDF'],
    },
    {
      icon: Zap,
      title: 'Lightning Fast Processing',
      description: 'Enterprise-grade conversion speeds with optimized engines and parallel processing capabilities.',
      highlights: ['Sub-second conversion', 'Batch processing', 'Parallel execution', 'CDN delivery'],
    },
    {
      icon: Shield,
      title: 'Enterprise Security',
      description: 'SOC2 compliant with end-to-end encryption, secure API keys, and comprehensive audit logs.',
      highlights: ['End-to-end encryption', 'SOC2 compliance', 'API key security', 'Audit logging'],
    },
    {
      icon: Code,
      title: 'Developer Friendly',
      description: 'RESTful APIs with comprehensive documentation, SDKs for popular languages, and excellent DX.',
      highlights: ['RESTful API', 'Multiple SDKs', 'OpenAPI spec', 'Interactive docs'],
    },
  ];
  
  const conversionTypes = Object.entries(CONVERSION_FORMATS).map(([key, format]) => {
    const iconMap = {
      FileText: FileText,
      Globe: Globe,
      BarChart3: BarChart3,
      GitCompare: GitCompare,
    };
    
    const Icon = iconMap[format.icon as keyof typeof iconMap] || FileText;
    
    return {
      key,
      ...format,
      Icon,
    };
  });
  
  const additionalFeatures = [
    {
      icon: Clock,
      title: '99.9% Uptime SLA',
      description: 'Reliable service with guaranteed uptime and 24/7 monitoring.',
    },
    {
      icon: BarChart3,
      title: 'Real-time Analytics',
      description: 'Detailed conversion metrics, usage analytics, and performance insights.',
    },
    {
      icon: GitCompare,
      title: 'Document Comparison',
      description: 'Advanced DOCX comparison with detailed difference analysis.',
    },
  ];
  
  return (
    <section id="features" className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
            Powerful Features for
            <span className="block gradient-text">Professional Document Conversion</span>
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Everything you need to convert, process, and manage documents at scale with 
            enterprise-grade reliability and performance.
          </p>
        </motion.div>
        
        {/* Main features grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-20">
          {mainFeatures.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
              >
                <Card className="h-full p-8 hover:shadow-strong transition-all duration-300 group">
                  <div className="flex items-start space-x-4">
                    <div className="flex-shrink-0">
                      <div className="w-12 h-12 bg-brand-100 rounded-xl flex items-center justify-center group-hover:bg-brand-200 transition-colors">
                        <Icon className="h-6 w-6 text-brand-600" />
                      </div>
                    </div>
                    
                    <div className="flex-1">
                      <h3 className="text-xl font-semibold text-gray-900 mb-3">
                        {feature.title}
                      </h3>
                      <p className="text-gray-600 mb-4 leading-relaxed">
                        {feature.description}
                      </p>
                      
                      <ul className="space-y-2">
                        {feature.highlights.map((highlight, idx) => (
                          <li key={idx} className="flex items-center space-x-2 text-sm text-gray-700">
                            <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0" />
                            <span>{highlight}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </Card>
              </motion.div>
            );
          })}
        </div>
        
        {/* Conversion types showcase */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="mb-20"
        >
          <div className="text-center mb-12">
            <h3 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-4">
              Supported Conversion Types
            </h3>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Convert between multiple document formats with professional quality and 
              preserved formatting.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {conversionTypes.map((conversion, index) => {
              const Icon = conversion.Icon;
              const colorClasses = {
                blue: 'from-blue-500 to-blue-600 bg-blue-100 text-blue-600',
                green: 'from-green-500 to-green-600 bg-green-100 text-green-600',
                purple: 'from-purple-500 to-purple-600 bg-purple-100 text-purple-600',
                orange: 'from-orange-500 to-orange-600 bg-orange-100 text-orange-600',
                red: 'from-red-500 to-red-600 bg-red-100 text-red-600',
              };
              
              const colorClass = colorClasses[conversion.color as keyof typeof colorClasses] || colorClasses.blue;
              
              return (
                <motion.div
                  key={conversion.key}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                >
                  <Card className="p-6 text-center hover:scale-105 transition-all duration-300 cursor-pointer group">
                    <div className={`w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-4 ${colorClass.split(' ')[2]} ${colorClass.split(' ')[3]}`}>
                      <Icon className="h-8 w-8" />
                    </div>
                    
                    <h4 className="text-lg font-semibold text-gray-900 mb-2">
                      {conversion.name}
                    </h4>
                    
                    <p className="text-sm text-gray-600 mb-4">
                      {conversion.description}
                    </p>
                    
                    <div className="text-xs text-gray-500">
                      <span className="inline-block px-2 py-1 bg-gray-100 rounded-full">
                        Output: {conversion.outputFormat}
                      </span>
                    </div>
                  </Card>
                </motion.div>
              );
            })}
          </div>
        </motion.div>
        
        {/* Additional features */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {additionalFeatures.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <motion.div
                  key={feature.title}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                  className="text-center"
                >
                  <div className="w-16 h-16 bg-gray-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                    <Icon className="h-8 w-8 text-gray-600" />
                  </div>
                  
                  <h4 className="text-lg font-semibold text-gray-900 mb-2">
                    {feature.title}
                  </h4>
                  
                  <p className="text-gray-600">
                    {feature.description}
                  </p>
                </motion.div>
              );
            })}
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default Features;