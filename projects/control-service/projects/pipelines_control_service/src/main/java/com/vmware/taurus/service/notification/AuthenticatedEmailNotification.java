package com.vmware.taurus.service.notification;

import java.util.Arrays;
import java.util.Properties;
import javax.mail.Address;
import javax.mail.Authenticator;
import javax.mail.MessagingException;
import javax.mail.PasswordAuthentication;
import javax.mail.SendFailedException;
import javax.mail.Session;
import javax.mail.Transport;
import javax.mail.internet.InternetAddress;
import javax.mail.internet.MimeMessage;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

@Service
@Slf4j
public class AuthenticatedEmailNotification {

  private EmailPropertiesConfiguration emailPropertiesConfiguration;
  private final Session session;
  private static final String CONTENT_TYPE = "text/html; charset=utf-8";


  public AuthenticatedEmailNotification(EmailPropertiesConfiguration emailPropertiesConfiguration) {
    this.emailPropertiesConfiguration = emailPropertiesConfiguration;
    Properties properties = new Properties();
    properties.setProperty("mail.transport.protocol", "smtp");
    properties.putAll(this.emailPropertiesConfiguration.smtpWithPrefix());
    session = Session.getInstance(properties,
        getAuthenticator(emailPropertiesConfiguration.getUsername(),
            emailPropertiesConfiguration.getPassword()));
  }


  public void send(NotificationContent notificationContent) throws MessagingException {
    try {
      sendAuthenticatedEmail(notificationContent, notificationContent.getRecipients());
    } catch (SendFailedException firstException) {
      log.error("First attempt to send notification failed", firstException);
      log.error("Failed to send notification due to: {}",
          firstException.getMessage());
      var addressesToRetry = firstException.getValidUnsentAddresses();
      try {
        sendAuthenticatedEmail(notificationContent, addressesToRetry);
      } catch (SendFailedException secondException) {
        log.error(
            "Failed to send message due to: {}, following emails did not receive a notification {}",
            secondException.getMessage(),
            Arrays.deepToString(secondException.getValidUnsentAddresses()));
      }
    }
  }

  private void sendAuthenticatedEmail(NotificationContent notificationContent, Address[] recipients)
      throws MessagingException {
    Transport transport = session.getTransport();
    var mimeMessage = prepareMessage(notificationContent);
    try {
      transport.connect();
      transport.send(mimeMessage, recipients);
    } finally {
      transport.close();
    }
  }

  private MimeMessage prepareMessage(NotificationContent notificationContent)
      throws MessagingException {
    MimeMessage mimeMessage = new MimeMessage(session);
    mimeMessage.setFrom(new InternetAddress(emailPropertiesConfiguration.getUsername()));
    mimeMessage.setSubject(notificationContent.getSubject());
    mimeMessage.setContent(notificationContent.getContent(), CONTENT_TYPE);
    return mimeMessage;
  }

  private static Authenticator getAuthenticator(String username, String password) {
    return new Authenticator() {
      @Override
      protected PasswordAuthentication getPasswordAuthentication() {
        return new PasswordAuthentication(username, password);
      }
    };
  }
}
