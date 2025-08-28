import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Check, ArrowRight, Star, Zap } from 'lucide-react';
import { Button, Card, CardContent } from '../common';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../stores';
import { SUBSCRIPTION_PLANS } from '../../constants';
import { cn } from '../../utils';

const Pricing: React.FC = () => {
  const [billingPeriod, setBillingPeriod] = useState<'monthly' | 'yearly'>('monthly');
  const navigate = useNavigate();
  const { isAuthenticated } = useAuthStore();
  
  const plans = Object.values(SUBSCRIPTION_PLANS);
  
  // Mock yearly discount (20% off)
  const getPrice = (monthlyPrice: number) => {
    if (billingPeriod === 'yearly') {
      return Math.round(monthlyPrice * 12 * 0.8); // 20% annual discount
    }
    return monthlyPrice;
  };
  
  const getPriceLabel = (monthlyPrice: number) => {
    if (billingPeriod === 'yearly') {
      return `$${getPrice(monthlyPrice)}/year`;
    }
    return monthlyPrice === 0 ? 'Free' : `$${monthlyPrice}/month`;
  };
  
  const handleGetStarted = (planId: string) => {
    if (isAuthenticated) {
      if (planId === 'free') {
        navigate('/convert');
      } else {
        navigate('/settings?tab=billing');
      }
    } else {
      navigate('/register?plan=' + planId);
    }
  };
  
  return (
    <section id="pricing" className="py-20 bg-gray-50">
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
            Simple, Transparent
            <span className="block gradient-text">Pricing</span>
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8">
            Choose the plan that fits your needs. Start free and scale as you grow.
            All plans include our core conversion features.
          </p>
          
          {/* Billing toggle */}
          <div className="inline-flex items-center bg-white rounded-lg p-1 shadow-sm border border-gray-200">
            <button
              onClick={() => setBillingPeriod('monthly')}
              className={cn(
                'px-4 py-2 rounded-md text-sm font-medium transition-all duration-200',
                billingPeriod === 'monthly'
                  ? 'bg-brand-600 text-white shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              )}
            >
              Monthly
            </button>
            <button
              onClick={() => setBillingPeriod('yearly')}
              className={cn(
                'px-4 py-2 rounded-md text-sm font-medium transition-all duration-200 relative',
                billingPeriod === 'yearly'
                  ? 'bg-brand-600 text-white shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              )}
            >
              Yearly
              <span className="absolute -top-2 -right-2 bg-green-500 text-white text-xs px-1.5 py-0.5 rounded-full">
                -20%
              </span>
            </button>
          </div>
        </motion.div>
        
        {/* Pricing cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          {plans.map((plan, index) => {
            const isPopular = plan.id === 'professional';
            const price = getPrice(plan.price);
            
            return (
              <motion.div
                key={plan.id}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className={cn(
                  'relative',
                  isPopular && 'md:-mt-4 md:mb-4'
                )}
              >
                {isPopular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2 z-10">
                    <div className="inline-flex items-center space-x-1 bg-brand-600 text-white px-3 py-1 rounded-full text-sm font-medium">
                      <Star className="h-4 w-4" />
                      <span>Most Popular</span>
                    </div>
                  </div>
                )}
                
                <Card 
                  className={cn(
                    'h-full relative overflow-hidden',
                    isPopular 
                      ? 'border-brand-200 shadow-strong ring-2 ring-brand-100' 
                      : 'border-gray-200 hover:shadow-medium'
                  )}
                >
                  {isPopular && (
                    <div className="absolute top-0 right-0 w-32 h-32 transform rotate-45 translate-x-16 -translate-y-16">
                      <div className="absolute bottom-0 left-0 w-full h-full bg-gradient-to-tr from-brand-400 to-brand-600 opacity-10" />
                    </div>
                  )}
                  
                  <CardContent className="p-8">
                    {/* Plan header */}
                    <div className="text-center mb-8">
                      <h3 className="text-xl font-semibold text-gray-900 mb-2">
                        {plan.name}
                      </h3>
                      
                      <div className="mb-4">
                        {plan.price === 0 ? (
                          <div className="text-4xl font-bold text-gray-900">
                            Free
                          </div>
                        ) : (
                          <div className="flex items-baseline justify-center">
                            <span className="text-4xl font-bold text-gray-900">
                              ${billingPeriod === 'yearly' ? Math.round(price / 12) : price}
                            </span>
                            <span className="text-lg text-gray-600 ml-1">
                              /{billingPeriod === 'yearly' ? 'month' : 'month'}
                            </span>
                          </div>
                        )}
                        
                        {billingPeriod === 'yearly' && plan.price > 0 && (
                          <div className="text-sm text-green-600 mt-1">
                            ${price}/year (save 20%)
                          </div>
                        )}
                      </div>
                      
                      <Button
                        variant={isPopular ? 'primary' : 'outline'}
                        className="w-full mb-6"
                        onClick={() => handleGetStarted(plan.id)}
                        rightIcon={<ArrowRight className="h-4 w-4" />}
                      >
                        {plan.id === 'free' ? 'Get Started' : 'Upgrade Now'}
                      </Button>
                    </div>
                    
                    {/* Features list */}
                    <div className="space-y-4">
                      <div className="text-sm font-medium text-gray-900 mb-3">
                        What's included:
                      </div>
                      
                      <ul className="space-y-3">
                        {plan.features.map((feature, idx) => (
                          <li key={idx} className="flex items-start space-x-3">
                            <Check className="h-5 w-5 text-green-500 flex-shrink-0 mt-0.5" />
                            <span className="text-sm text-gray-700">
                              {feature}
                            </span>
                          </li>
                        ))}
                      </ul>
                      
                      {/* Plan limits */}
                      <div className="pt-4 border-t border-gray-200">
                        <div className="text-xs text-gray-500 space-y-1">
                          <div className="flex justify-between">
                            <span>Monthly conversions:</span>
                            <span className="font-medium">
                              {plan.limits.conversions_per_month === -1 
                                ? 'Unlimited' 
                                : plan.limits.conversions_per_month.toLocaleString()}
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span>Max file size:</span>
                            <span className="font-medium">
                              {Math.round(plan.limits.max_file_size / (1024 * 1024))}MB
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span>API access:</span>
                            <span className="font-medium">
                              {plan.limits.api_access ? 'Yes' : 'No'}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            );
          })}
        </div>
        
        {/* Enterprise CTA */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="mt-16 text-center"
        >
          <Card className="p-8 bg-gradient-to-r from-gray-900 to-gray-800 text-white border-0">
            <div className="max-w-3xl mx-auto">
              <div className="flex items-center justify-center mb-4">
                <Zap className="h-8 w-8 text-brand-400 mr-3" />
                <h3 className="text-2xl font-bold">
                  Need Something Custom?
                </h3>
              </div>
              
              <p className="text-lg text-gray-300 mb-6">
                Looking for custom integrations, higher limits, or on-premises deployment? 
                We'll work with you to create a solution that fits your specific needs.
              </p>
              
              <div className="flex flex-col sm:flex-row items-center justify-center space-y-3 sm:space-y-0 sm:space-x-4">
                <Button
                  variant="outline"
                  className="bg-white text-gray-900 border-white hover:bg-gray-100"
                  onClick={() => navigate('/contact')}
                >
                  Contact Sales
                </Button>
                
                <Button
                  variant="ghost"
                  className="text-white hover:bg-white/10"
                  onClick={() => navigate('/enterprise')}
                >
                  View Enterprise Features
                </Button>
              </div>
            </div>
          </Card>
        </motion.div>
        
        {/* FAQ link */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.6 }}
          className="mt-12 text-center"
        >
          <p className="text-gray-600">
            Have questions about pricing? 
            <button 
              onClick={() => navigate('/faq')}
              className="text-brand-600 hover:text-brand-700 font-medium ml-1"
            >
              Check our FAQ
            </button>
          </p>
        </motion.div>
      </div>
    </section>
  );
};

export default Pricing;