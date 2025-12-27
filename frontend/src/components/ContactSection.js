import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Mail, Phone, Send, MessageCircle, MessageSquare } from 'lucide-react';
import { useToast } from '../hooks/use-toast';
import LinkedInBadge from './LinkedInBadge';

const ContactSection = ({ personalInfo }) => {
  const [formData, setFormData] = useState({ name: '', email: '', subject: '', message: '' });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isVisible, setIsVisible] = useState(false);
  const sectionRef = useRef(null);
  const { toast } = useToast();

  useEffect(() => {
    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) {
        setIsVisible(true);
        observer.unobserve(entry.target);
      }
    }, { threshold: 0.1 });

    if (sectionRef.current) {
      observer.observe(sectionRef.current);
    }
    return () => {
      if (sectionRef.current) {
        observer.unobserve(sectionRef.current);
      }
    };
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

    const payload = {
      name: formData.name,
      email: formData.email,
      subject: formData.subject,
      message: formData.message,
    };

    try {
      const apiUrl = `${process.env.REACT_APP_API_URL || 'https://althaf-portfolio.onrender.com'}/api/contact`;

      const response = await axios.post(apiUrl, payload);

      toast({
        title: "Message Sent Successfully!",
        description: "Thank you for reaching out. I'll get back to you soon.",
      });

      setFormData({ name: '', email: '', subject: '', message: '' });

    } catch (error) {
      toast({
        title: "Error Sending Message",
        description: error.response?.data?.detail || "Something went wrong. Please try again later.",
        variant: "destructive",
      });
      console.error('Error submitting form:', error.response?.data || error.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const phoneNumber = personalInfo.phone.replace(/\D/g, '');
  const prefilledMessage = "Hello Althaf, I saw your portfolio and would like to connect!";
  const whatsappUrl = `https://wa.me/91${phoneNumber}?text=${encodeURIComponent(prefilledMessage)}`;

  return (
    <section id="contact" className="py-20 bg-background relative overflow-hidden" ref={sectionRef}>
      <div className="absolute inset-0 overflow-hidden">
        <div className="bg-orb bg-orb-1"></div>
        <div className="bg-orb bg-orb-2"></div>
        <div className="bg-orb bg-orb-3"></div>
      </div>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="text-center mb-16">
          <h2 className={`text-3xl md:text-4xl font-bold mb-4 text-foreground shine-text ${isVisible ? 'fade-in-up' : ''}`}>Let's Connect</h2>
          <p className={`text-lg text-muted-foreground max-w-3xl mx-auto glow-text ${isVisible ? 'fade-in-up stagger-1' : ''}`}>Ready to discuss your next DevOps project or explore opportunities? I'd love to hear from you!</p>
        </div>
        <div className="grid lg:grid-cols-2 gap-12">
          <div className={`space-y-8 ${isVisible ? 'fade-in-left stagger-2' : ''}`}>
            <div>
              <h3 className="text-2xl font-semibold mb-6 text-foreground shine-text-slow">Get in Touch</h3>
              <p className="text-muted-foreground mb-8 text-lg leading-relaxed glow-text">I'm always interested in hearing about new opportunities, collaborating on exciting projects, or discussing the latest in DevOps and cloud technologies. Feel free to reach out!</p>
            </div>
            <div className="space-y-4">
              <Card className={`p-4 neon-card transition-all ${isVisible ? 'scale-in stagger-3' : ''}`}>
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-cyan-400/10 rounded-lg flex items-center justify-center border border-cyan-400/30"><Mail className="w-6 h-6 text-cyan-soft" /></div>
                  <div>
                    <h4 className="font-semibold text-foreground">Email</h4>
                    <a href={`mailto:${personalInfo.email}`} className="text-cyan-soft hover:underline">{personalInfo.email}</a>
                  </div>
                </div>
              </Card>
              <Card className={`p-4 neon-card transition-all ${isVisible ? 'scale-in stagger-4' : ''}`}>
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-green-400/10 rounded-lg flex items-center justify-center border border-green-400/30"><Phone className="w-6 h-6 text-green-soft" /></div>
                  <div>
                    <h4 className="font-semibold text-foreground">Phone</h4>
                    <a href={`tel:${personalInfo.phone}`} className="text-green-soft hover:underline">{personalInfo.phone}</a>
                  </div>
                </div>
              </Card>
              <Card className={`p-4 neon-card transition-all ${isVisible ? 'scale-in stagger-5' : ''}`}>
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-purple-400/10 rounded-lg flex items-center justify-center border border-purple-400/30">
                    <MessageSquare className="w-6 h-6 text-purple-soft" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-foreground">WhatsApp</h4>
                    <a href={whatsappUrl} target="_blank" rel="noopener noreferrer" className="text-purple-soft hover:underline">Chat with me</a>
                  </div>
                </div>
              </Card>
            </div>

            <div className="mt-8">
              <LinkedInBadge />
            </div>
          </div>
          <Card className={`p-8 neon-card ${isVisible ? 'fade-in-right stagger-8' : ''}`}>
            <div className="flex items-center space-x-3 mb-6">
              <div className="w-10 h-10 bg-cyan-400/10 rounded-lg flex items-center justify-center border border-cyan-400/30"><MessageCircle className="w-5 h-5 text-cyan-soft" /></div>
              <h3 className="text-xl font-semibold text-foreground">Send me a message</h3>
            </div>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="name" className="block text-sm font-medium text-muted-foreground mb-2">Your Name</label>
                  <Input id="name" name="name" type="text" autoComplete="name" value={formData.name} onChange={handleInputChange} placeholder="Enter your full name" required className="form-input" />
                </div>
                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-muted-foreground mb-2">Email Address</label>
                  <Input id="email" name="email" type="email" autoComplete="email" value={formData.email} onChange={handleInputChange} placeholder="your.email@example.com" required className="form-input" />
                </div>
              </div>
              <div>
                <label htmlFor="subject" className="block text-sm font-medium text-muted-foreground mb-2">Subject</label>
                <Input id="subject" name="subject" type="text" value={formData.subject} onChange={handleInputChange} placeholder="What's this about?" className="form-input" />
              </div>
              <div>
                <label htmlFor="message" className="block text-sm font-medium text-muted-foreground mb-2">Message</label>
                <Textarea id="message" name="message" value={formData.message} onChange={handleInputChange} placeholder="Tell me about your project..." rows={6} required className="form-input" />
              </div>
              <Button type="submit" disabled={isSubmitting} className="w-full neon-button bg-gradient-to-r from-cyan-500 to-pink-500 text-black py-3 text-lg font-bold disabled:opacity-50">
                {isSubmitting ? 'Sending...' : <><Send className="w-5 h-5 mr-3" />Send Message</>}
              </Button>
            </form>
          </Card>
        </div>
      </div>
    </section>
  );
};
export default ContactSection;
