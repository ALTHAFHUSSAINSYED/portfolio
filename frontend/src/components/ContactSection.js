import React, { useState, useEffect, useRef } from 'react';
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
  const [isVisible, setIsVisible] = useState(false);
  const sectionRef = useRef(null);
  const { toast } = useToast();

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
        }
      },
      { threshold: 0.1 }
    );

    if (sectionRef.current) {
      observer.observe(sectionRef.current);
    }

    return () => observer.disconnect();
  }, []);

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
    try {
      const link = document.createElement('a');
      link.href = `${process.env.PUBLIC_URL || ''}/ALTHAF_HUSSAIN_SYED_DevOps_Resume.pdf`;
      link.download = 'Althaf_Hussain_Syed_DevOps_Resume.pdf';
      link.style.display = 'none';
      
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      console.log('Resume download initiated from contact section');
    } catch (error) {
      console.error('Download error:', error);
      window.open(`${process.env.PUBLIC_URL || ''}/ALTHAF_HUSSAIN_SYED_DevOps_Resume.pdf`, '_blank');
    }
  };

  return (
    <section id="contact" className="py-20 bg-black relative overflow-hidden" ref={sectionRef}>
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="bg-orb bg-orb-1"></div>
        <div className="bg-orb bg-orb-2"></div>
        <div className="bg-orb bg-orb-3"></div>
        
        {/* Contact-themed floating elements */}
        <div className="absolute top-1/4 left-1/6 w-4 h-4 bg-cyan-400/20 rounded-full floating opacity-40"></div>
        <div className="absolute bottom-1/4 right-1/6 w-6 h-6 bg-pink-500/20 rounded-full bounce-glow opacity-30"></div>
        <div className="absolute top-2/3 left-2/3 w-3 h-3 bg-green-400/20 rounded-full floating-reverse opacity-35"></div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="text-center mb-16">
          <h2 className={`text-3xl md:text-4xl font-bold mb-4 shine-text ${isVisible ? 'fade-in-up' : ''}`}>
            Let's Connect
          </h2>
          <p className={`text-lg text-gray-300 max-w-3xl mx-auto glow-text ${isVisible ? 'fade-in-up stagger-1' : ''}`}>
            Ready to discuss your next DevOps project or explore opportunities? I'd love to hear from you!
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-12">
          {/* Contact Information */}
          <div className={`space-y-8 ${isVisible ? 'fade-in-left stagger-2' : ''}`}>
            <div>
              <h3 className="text-2xl font-semibold mb-6 shine-text-slow">
                Get in Touch
              </h3>
              <p className="text-gray-300 mb-8 text-lg leading-relaxed glow-text">
                I'm always interested in hearing about new opportunities, collaborating on exciting projects, 
                or discussing the latest in DevOps and cloud technologies. Feel free to reach out!
              </p>
            </div>

            {/* Contact Methods */}
            <div className="space-y-4">
              <Card className={`p-4 bg-black/80 border border-gray-700/30 hover:border-cyan-400/40 transition-all duration-300 backdrop-blur-sm neon-card hover-lift hover-shine ${
                isVisible ? 'scale-in stagger-3' : ''
              }`}>
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-cyan-400/10 rounded-lg flex items-center justify-center border border-cyan-400/30 pulse-shine">
                    <Mail className="w-6 h-6 text-cyan-soft" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-white sparkle-text">Email</h4>
                    <a 
                      href={`mailto:${personalInfo.email}`}
                      className="text-cyan-soft hover:text-cyan-400 transition-colors hover:underline glow-text"
                    >
                      {personalInfo.email}
                    </a>
                  </div>
                </div>
              </Card>

              <Card className={`p-4 bg-black/80 border border-gray-700/30 hover:border-green-400/40 transition-all duration-300 backdrop-blur-sm neon-card hover-lift hover-shine ${
                isVisible ? 'scale-in stagger-4' : ''
              }`}>
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-green-400/10 rounded-lg flex items-center justify-center border border-green-400/30 pulse-shine">
                    <Phone className="w-6 h-6 text-green-soft" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-white sparkle-text">Phone</h4>
                    <a 
                      href={`tel:${personalInfo.phone}`}
                      className="text-green-soft hover:text-green-400 transition-colors hover:underline glow-text"
                    >
                      {personalInfo.phone}
                    </a>
                  </div>
                </div>
              </Card>

              <Card className={`p-4 bg-black/80 border border-gray-700/30 hover:border-purple-400/40 transition-all duration-300 backdrop-blur-sm neon-card hover-lift hover-shine ${
                isVisible ? 'scale-in stagger-5' : ''
              }`}>
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-purple-400/10 rounded-lg flex items-center justify-center border border-purple-400/30 pulse-shine">
                    <MapPin className="w-6 h-6 text-purple-soft" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-white sparkle-text">Location</h4>
                    <p className="text-gray-300 glow-text">{personalInfo.location}</p>
                  </div>
                </div>
              </Card>

              <Card className={`p-4 bg-black/80 border border-gray-700/30 hover:border-blue-400/40 transition-all duration-300 backdrop-blur-sm neon-card hover-lift hover-shine ${
                isVisible ? 'scale-in stagger-6' : ''
              }`}>
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-blue-400/10 rounded-lg flex items-center justify-center border border-blue-400/30 pulse-shine">
                    <Linkedin className="w-6 h-6 text-blue-soft" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-white sparkle-text">LinkedIn</h4>
                    <a 
                      href={personalInfo.linkedin}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-soft hover:text-blue-400 transition-colors hover:underline glow-text"
                    >
                      Connect on LinkedIn
                    </a>
                  </div>
                </div>
              </Card>
            </div>

            {/* Quick Actions */}
            <div className={`space-y-3 ${isVisible ? 'fade-in-up stagger-7' : ''}`}>
              <Button
                onClick={downloadResume}
                className="w-full neon-button bg-gradient-to-r from-cyan-500/80 to-pink-500/80 hover:from-cyan-500 hover:to-pink-500 text-black py-3 text-lg font-bold transition-all duration-300"
              >
                <Download className="w-5 h-5 mr-3" />
                Download My Resume
              </Button>
              <Button
                onClick={() => window.open(personalInfo.linkedin, '_blank')}
                variant="outline"
                className="w-full border-cyan-400/50 text-cyan-soft bg-black/50 hover:bg-cyan-400/10 hover:text-cyan-400 py-3 text-lg font-medium hover-lift transition-all duration-300 backdrop-blur-sm sparkle-text"
              >
                <Linkedin className="w-5 h-5 mr-3" />
                View LinkedIn Profile
              </Button>
            </div>
          </div>

          {/* Contact Form */}
          <Card className={`p-8 bg-black/80 border border-gray-700/30 backdrop-blur-sm neon-card hover-lift ${
            isVisible ? 'fade-in-right stagger-8' : ''
          }`}>
            <div className="flex items-center space-x-3 mb-6">
              <div className="w-10 h-10 bg-cyan-400/10 rounded-lg flex items-center justify-center border border-cyan-400/30 pulse-shine">
                <MessageCircle className="w-5 h-5 text-cyan-soft" />
              </div>
              <h3 className="text-xl font-semibold text-white shine-text-slow">
                Send me a message
              </h3>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="name" className="block text-sm font-medium text-gray-300 mb-2 sparkle-text">
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
                    className="form-input border-gray-600/50 focus:border-cyan-400/80 focus:ring-cyan-400/20 bg-black/50 text-white placeholder-gray-400"
                  />
                </div>
                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-gray-300 mb-2 sparkle-text">
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
                    className="form-input border-gray-600/50 focus:border-cyan-400/80 focus:ring-cyan-400/20 bg-black/50 text-white placeholder-gray-400"
                  />
                </div>
              </div>

              <div>
                <label htmlFor="subject" className="block text-sm font-medium text-gray-300 mb-2 sparkle-text">
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
                  className="form-input border-gray-600/50 focus:border-cyan-400/80 focus:ring-cyan-400/20 bg-black/50 text-white placeholder-gray-400"
                />
              </div>

              <div>
                <label htmlFor="message" className="block text-sm font-medium text-gray-300 mb-2 sparkle-text">
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
                  className="form-input border-gray-600/50 focus:border-cyan-400/80 focus:ring-cyan-400/20 bg-black/50 text-white placeholder-gray-400 resize-none"
                />
              </div>

              <Button
                type="submit"
                disabled={isSubmitting}
                className="w-full neon-button bg-gradient-to-r from-cyan-500/80 to-pink-500/80 hover:from-cyan-500 hover:to-pink-500 text-black py-3 text-lg font-bold transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isSubmitting ? (
                  <div className="flex items-center justify-center">
                    <div className="loading-dots mr-3">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
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
        <div className={`mt-16 text-center bg-black/60 rounded-xl p-8 border border-gray-700/30 backdrop-blur-sm neon-card hover-lift ${
          isVisible ? 'slide-in-bottom stagger-8' : ''
        }`}>
          <h3 className="text-xl font-semibold mb-4 shine-text">
            Currently Available for New Opportunities
          </h3>
          <p className="text-gray-300 max-w-2xl mx-auto leading-relaxed glow-text">
            I'm actively exploring exciting DevOps and cloud engineering roles where I can contribute to 
            building scalable, reliable infrastructure. Let's discuss how my expertise can help your team succeed!
          </p>
        </div>
      </div>
    </section>
  );
};

export default ContactSection;