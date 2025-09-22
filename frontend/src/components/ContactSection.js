// src/components/ContactSection.js (Corrected handleSubmit function)

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    // ✨ CORRECTED: The keys now match the backend model (name, email, etc.)
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
        description: "Something went wrong. Please try again later.",
        variant: "destructive",
      });
      console.error('Error submitting form:', error.response?.data || error.message);
    } finally {
      setIsSubmitting(false);
    }
  };
