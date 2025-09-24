import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
// ✨ NEW: Imported MessageSquare for the WhatsApp icon
import { Mail, Phone, Send, MessageCircle, MessageSquare } from 'lucide-react'; 
import { useToast } from '../hooks/use-toast';

const ContactSection = ({ personalInfo }) => {
  const [formData, setFormData] = useState({ name: '', email: '', subject: '', message: '' });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isVisible, setIsVisible] = useState(false);
  const sectionRef = useRef(null);
  const { toast } = useToast();

  useEffect(() => {
    // ... (your existing useEffect observer logic)
  }, []);

  const handleInputChange = (e) => {
    // ... (your existing input change handler)
  };

  const handleSubmit = async (e) => {
    // ... (your existing form submit handler)
  };
  
  // ✨ NEW: WhatsApp URL generation
  const phoneNumber = personalInfo.phone.replace(/\D/g, ''); // Removes non-digit characters
  const prefilledMessage = "Hello Althaf, I saw your portfolio and would like to connect!";
  const whatsappUrl = `https://wa.me/${phoneNumber}?text=${encodeURIComponent(prefilledMessage)}`;


  return (
    <section id="contact" className="py-20 bg-background relative overflow-hidden" ref={sectionRef}>
      {/* ... (your existing background orbs) ... */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="text-center mb-16">
          {/* ... (your existing header text) ... */}
        </div>
        <div className="grid lg:grid-cols-2 gap-12">
          <div className={`space-y-8 ${isVisible ? 'fade-in-left stagger-2' : ''}`}>
            <div>
              {/* ... (your existing "Get in Touch" text) ... */}
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
              {/* ✨ NEW: WhatsApp Contact Card */}
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
          </div>
          <Card className={`p-8 neon-card ${isVisible ? 'fade-in-right stagger-8' : ''}`}>
            {/* ... (your existing contact form) ... */}
          </Card>
        </div>
      </div>
    </section>
  );
};
export default ContactSection;
