package com.vmware.taurus.service.notification;


import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.service.model.JobConfig;
import java.util.Collections;
import java.util.List;
import javax.mail.MessagingException;
import javax.mail.internet.AddressException;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.TestPropertySource;

@SpringBootTest(classes = ControlplaneApplication.class)
@TestPropertySource(
    properties = {
        "mail.smtp.host=smtp.vmware.com",
        "mail.smtp.auth=true",
        "mail.smtp.starttls.enable=true",
        "mail.transport.protocol=smtp",
        "mail.smtp.user=",
        "mail.smtp.password="
    })
@Disabled("Placeholder for manual testing.")
public class AuthenticatedEmailNotificationTest {

    @Autowired
    private AuthenticatedEmailNotification authenticatedEmailNotification;

    @Test
    public void manualTestMultiple() throws MessagingException {
        authenticatedEmailNotification.send(createNotification(Collections.singletonList("")));
        authenticatedEmailNotification.send(createNotification(Collections.singletonList("")));
    }

    @Test
    public void manualSingle() throws MessagingException {
        authenticatedEmailNotification.send(createNotification(Collections.singletonList("")));
    }

    @Test
    public void sendMultiple() throws MessagingException {
        authenticatedEmailNotification.send(createNotification(List.of("", "")));

    }

    private NotificationContent createNotification(List<String> receivers) throws AddressException {
        NotificationContent notificationContent =
            new NotificationContent(
                createValidJobConfigStub(receivers),
                "run",
                "failure",
                "RuntimeError",
                "Some body",
                "Super Collider",
                "super-collider-data-pipelines@vmware.com",
                Collections.emptyList());
        return notificationContent;
    }

    private JobConfig createValidJobConfigStub(List<String> receivers) {
        JobConfig jobConfig = new JobConfig();
        jobConfig.setNotifiedOnJobDeploy(receivers);
        jobConfig.setJobName("test_job");
        return jobConfig;
    }

}
