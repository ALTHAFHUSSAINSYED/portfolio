import React, { useState } from 'react';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Award, Calendar, Filter } from 'lucide-react';

const CertificationsSection = ({ certifications }) => {
  const [selectedCategory, setSelectedCategory] = useState('all');

  const categories = {
    all: { name: 'All Certifications', color: 'text-gray-700', bg: 'bg-gray-100' },
    aws: { name: 'AWS', color: 'text-orange-600', bg: 'bg-orange-50' },
    gcp: { name: 'Google Cloud', color: 'text-blue-600', bg: 'bg-blue-50' },
    azure: { name: 'Microsoft Azure', color: 'text-blue-700', bg: 'bg-blue-50' },
    oracle: { name: 'Oracle', color: 'text-red-600', bg: 'bg-red-50' },
    devops: { name: 'DevOps', color: 'text-green-600', bg: 'bg-green-50' },
    ai: { name: 'AI/ML', color: 'text-purple-600', bg: 'bg-purple-50' }
  };

  const filteredCertifications = selectedCategory === 'all' 
    ? certifications 
    : certifications.filter(cert => cert.category === selectedCategory);

  const getCertificationIcon = (category) => {
    return <Award className="w-6 h-6" />;
  };

  const getCertificationColor = (category) => {
    return categories[category]?.color || 'text-gray-600';
  };

  const getCertificationBg = (category) => {
    return categories[category]?.bg || 'bg-gray-50';
  };

  return (
    <section id="certifications" className="py-20 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Certifications & Credentials
          </h2>
          <p className="text-lg text-gray-600 max-w-3xl mx-auto">
            Industry-recognized certifications across multiple cloud platforms and technologies
          </p>
        </div>

        {/* Filter Buttons */}
        <div className="flex flex-wrap justify-center gap-3 mb-12">
          {Object.entries(categories).map(([key, category]) => (
            <Button
              key={key}
              onClick={() => setSelectedCategory(key)}
              variant={selectedCategory === key ? 'default' : 'outline'}
              size="sm"
              className={`transition-all duration-200 ${
                selectedCategory === key 
                  ? 'bg-blue-600 hover:bg-blue-700 text-white' 
                  : 'border-gray-200 text-gray-700 hover:bg-gray-50'
              }`}
            >
              <Filter className="w-4 h-4 mr-2" />
              {category.name}
            </Button>
          ))}
        </div>

        {/* Certifications Count */}
        <div className="text-center mb-8">
          <Badge variant="outline" className="border-blue-200 text-blue-700 bg-blue-50 px-4 py-2 text-lg">
            {filteredCertifications.length} {selectedCategory === 'all' ? 'Total' : categories[selectedCategory]?.name} Certifications
          </Badge>
        </div>

        {/* Certifications Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredCertifications.map((cert, index) => (
            <Card 
              key={index} 
              className="p-6 border border-gray-100 hover:border-blue-200 hover:shadow-lg transition-all duration-200 bg-white group"
            >
              <div className="flex items-start space-x-4">
                <div className={`w-12 h-12 rounded-lg flex items-center justify-center flex-shrink-0 ${getCertificationBg(cert.category)} group-hover:scale-110 transition-transform`}>
                  <div className={getCertificationColor(cert.category)}>
                    {getCertificationIcon(cert.category)}
                  </div>
                </div>
                
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-gray-900 mb-2 leading-tight group-hover:text-blue-700 transition-colors">
                    {cert.name}
                  </h3>
                  <p className="text-gray-600 text-sm mb-3 font-medium">
                    {cert.issuer}
                  </p>
                  <div className="flex items-center text-gray-500 text-sm">
                    <Calendar className="w-4 h-4 mr-2" />
                    <span>{cert.year}</span>
                  </div>
                </div>
              </div>
              
              <div className="mt-4 pt-4 border-t border-gray-100">
                <Badge 
                  variant="outline" 
                  className={`${getCertificationBg(cert.category)} ${getCertificationColor(cert.category)} border-current text-xs px-2 py-1`}
                >
                  {categories[cert.category]?.name || cert.category}
                </Badge>
              </div>
            </Card>
          ))}
        </div>

        {/* Certification Summary Stats */}
        <div className="mt-16 bg-white rounded-xl p-8 shadow-sm border border-gray-100">
          <h3 className="text-2xl font-bold text-gray-900 text-center mb-8">
            Certification Portfolio Overview
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div className="text-center p-4 bg-orange-50 rounded-lg border border-orange-100">
              <div className="text-2xl font-bold text-orange-600 mb-2">
                {certifications.filter(c => c.category === 'aws').length}
              </div>
              <div className="text-gray-600 font-medium text-sm">AWS Certs</div>
            </div>
            <div className="text-center p-4 bg-blue-50 rounded-lg border border-blue-100">
              <div className="text-2xl font-bold text-blue-600 mb-2">
                {certifications.filter(c => c.category === 'gcp').length}
              </div>
              <div className="text-gray-600 font-medium text-sm">GCP Certs</div>
            </div>
            <div className="text-center p-4 bg-blue-50 rounded-lg border border-blue-100">
              <div className="text-2xl font-bold text-blue-700 mb-2">
                {certifications.filter(c => c.category === 'azure').length}
              </div>
              <div className="text-gray-600 font-medium text-sm">Azure Certs</div>
            </div>
            <div className="text-center p-4 bg-red-50 rounded-lg border border-red-100">
              <div className="text-2xl font-bold text-red-600 mb-2">
                {certifications.filter(c => c.category === 'oracle').length}
              </div>
              <div className="text-gray-600 font-medium text-sm">Oracle Certs</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default CertificationsSection;