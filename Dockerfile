# Start from a base AlmaLinux image
FROM almalinux:latest

# Update system and install Apache and necessary tools
RUN dnf update -y && \
    dnf install -y httpd zip unzip && \
    dnf clean all

# Add a valid zip file from a reliable source
ADD https://github.com/startbootstrap/startbootstrap-freelancer/archive/refs/heads/master.zip /var/www/html/

# Set the working directory
WORKDIR /var/www/html/

# Unzip and prepare the web files
RUN unzip master.zip && \
    cp -rvf startbootstrap-freelancer-master/* . && \
    rm -rf startbootstrap-freelancer-master master.zip
    
# Set Apache to run in the foreground
CMD ["/usr/sbin/httpd", "-D", "FOREGROUND"]

# Expose ports
EXPOSE 80 22
