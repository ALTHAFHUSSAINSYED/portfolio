import React, { useState } from 'react';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Mail, Phone, MapPin, Linkedin, Send, Download, MessageCircle } from 'lucide-react';
import { useToast } from '../hooks/use-toast';

const ContactSection = ({ personalInfo }) => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { toast } = useToast();

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    // Simulate form submission
    setTimeout(() => {
      toast({
        title: "Message Sent Successfully!",
        description: "Thank you for reaching out. I'll get back to you within 24 hours.",
      });
      
      setFormData({
        name: '',
        email: '',
        subject: '',
        message: ''
      });
      setIsSubmitting(false);
    }, 1000);
  };

  const downloadResume = () => {
    // In a real implementation, this would download the actual resume
    alert('Resume download feature - to be implemented with actual resume file');
  };

  return (
    <section id="contact" className="py-20 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Let's Connect
          </h2>
          <p className="text-lg text-gray-600 max-w-3xl mx-auto">
            Ready to discuss your next DevOps project or explore opportunities? I'd love to hear from you!
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-12">
          {/* Contact Information */}
          <div className="space-y-8">
            <div>
              <h3 className="text-2xl font-semibold text-gray-900 mb-6">
                Get in Touch
              </h3>
              <p className="text-gray-600 mb-8 text-lg leading-relaxed">
                I'm always interested in hearing about new opportunities, collaborating on exciting projects, 
                or discussing the latest in DevOps and cloud technologies. Feel free to reach out!
              </p>
            </div>

            {/* Contact Methods */}
            <div className="space-y-4">
              <Card className="p-4 border border-gray-100 hover:border-blue-200 hover:shadow-md transition-all duration-200 bg-white">
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-blue-50 rounded-lg flex items-center justify-center">
                    <Mail className="w-6 h-6 text-blue-600" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900">Email</h4>
                    <a 
                      href={`mailto:${personalInfo.email}`}
                      className="text-blue-600 hover:text-blue-700 transition-colors hover:underline"
                    >
                      {personalInfo.email}
                    </a>
                  </div>
                </div>
              </Card>

              <Card className="p-4 border border-gray-100 hover:border-blue-200 hover:shadow-md transition-all duration-200 bg-white">
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-green-50 rounded-lg flex items-center justify-center">
                    <Phone className="w-6 h-6 text-green-600" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900">Phone</h4>
                    <a 
                      href={`tel:${personalInfo.phone}`}
                      className="text-green-600 hover:text-green-700 transition-colors hover:underline"
                    >
                      {personalInfo.phone}
                    </a>
                  </div>
                </div>
              </Card>

              <Card className="p-4 border border-gray-100 hover:border-blue-200 hover:shadow-md transition-all duration-200 bg-white">
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-purple-50 rounded-lg flex items-center justify-center">
                    <MapPin className="w-6 h-6 text-purple-600" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900">Location</h4>
                    <p className="text-gray-600">{personalInfo.location}</p>
                  </div>
                </div>
              </Card>

              <Card className="p-4 border border-gray-100 hover:border-blue-200 hover:shadow-md transition-all duration-200 bg-white">
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-blue-50 rounded-lg flex items-center justify-center">
                    <Linkedin className="w-6 h-6 text-blue-600" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900">LinkedIn</h4>
                    <a 
                      href={personalInfo.linkedin}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-700 transition-colors hover:underline"
                    >
                      Connect on LinkedIn
                    </a>
                  </div>
                </div>
              </Card>
            </div>

            {/* Quick Actions */}
            <div className="space-y-3">
              <Button
                onClick={downloadResume}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 text-lg font-medium hover:shadow-lg transition-all duration-200"
              >
                <Download className="w-5 h-5 mr-3" />
                Download My Resume
              </Button>
              <Button
                onClick={() => window.open(personalInfo.linkedin, '_blank')}
                variant="outline"
                className="w-full border-blue-200 text-blue-700 hover:bg-blue-50 hover:border-blue-300 py-3 text-lg font-medium hover:shadow-lg transition-all duration-200"
              >
                <Linkedin className="w-5 h-5 mr-3" />
                View LinkedIn Profile
              </Button>
            </div>
          </div>

          {/* Contact Form */}
          <Card className="p-8 border border-gray-100 bg-white shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-center space-x-3 mb-6">
              <div className="w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center">
                <MessageCircle className="w-5 h-5 text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900">
                Send me a message
              </h3>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
                    Your Name
                  </label>
                  <Input
                    id="name"
                    name="name"
                    type="text"
                    value={formData.name}
                    onChange={handleInputChange}
                    placeholder="Enter your full name"
                    required
                    className="border-gray-200 focus:border-blue-300 focus:ring-blue-200"
                  />
                </div>
                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                    Email Address
                  </label>
                  <Input
                    id="email"
                    name="email"
                    type="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    placeholder="your.email@example.com"
                    required
                    className="border-gray-200 focus:border-blue-300 focus:ring-blue-200"
                  />
                </div>
              </div>

              <div>
                <label htmlFor="subject" className="block text-sm font-medium text-gray-700 mb-2">
                  Subject
                </label>
                <Input
                  id="subject"
                  name="subject"
                  type="text"
                  value={formData.subject}
                  onChange={handleInputChange}
                  placeholder="What's this about?"
                  required
                  className="border-gray-200 focus:border-blue-300 focus:ring-blue-200"
                />
              </div>

              <div>
                <label htmlFor="message" className="block text-sm font-medium text-gray-700 mb-2">
                  Message
                </label>
                <Textarea
                  id="message"
                  name="message"
                  value={formData.message}
                  onChange={handleInputChange}
                  placeholder="Tell me about your project or how I can help..."
                  rows={6}
                  required
                  className="border-gray-200 focus:border-blue-300 focus:ring-blue-200 resize-none"
                />
              </div>

              <Button
                type="submit"
                disabled={isSubmitting}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 text-lg font-medium hover:shadow-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isSubmitting ? (
                  <div className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-3"></div>
                    Sending...
                  </div>
                ) : (
                  <>
                    <Send className="w-5 h-5 mr-3" />
                    Send Message
                  </>
                )}
              </Button>
            </form>
          </Card>
        </div>

        {/* Availability Notice */}
        <div className="mt-16 text-center bg-white rounded-xl p-8 shadow-sm border border-gray-100">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">
            Currently Available for New Opportunities
          </h3>
          <p className="text-gray-600 max-w-2xl mx-auto leading-relaxed">
            I'm actively exploring exciting DevOps and cloud engineering roles where I can contribute to 
            building scalable, reliable infrastructure. Let's discuss how my expertise can help your team succeed!
          </p>
        </div>
      </div>
    </section>
  );
};

export default ContactSection;