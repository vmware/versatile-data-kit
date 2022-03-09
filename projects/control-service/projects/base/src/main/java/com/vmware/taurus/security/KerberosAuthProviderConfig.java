/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.security;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.annotation.Order;
import org.springframework.core.io.FileSystemResource;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.config.annotation.authentication.builders.AuthenticationManagerBuilder;
import org.springframework.security.config.annotation.method.configuration.EnableGlobalMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.builders.WebSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configuration.WebSecurityConfigurerAdapter;
import org.springframework.security.core.authority.AuthorityUtils;
import org.springframework.security.core.userdetails.User;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.security.kerberos.authentication.KerberosServiceAuthenticationProvider;
import org.springframework.security.kerberos.authentication.sun.SunJaasKerberosTicketValidator;
import org.springframework.security.kerberos.web.authentication.SpnegoAuthenticationProcessingFilter;
import org.springframework.security.web.authentication.www.BasicAuthenticationFilter;

//@Configuration
//@EnableWebSecurity
//@EnableGlobalMethodSecurity(prePostEnabled = true)
//@Order(101)
//@ConditionalOnProperty(value = "datajobs.security.kerberos.enabled")
public class KerberosAuthProviderConfig extends WebSecurityConfigurerAdapter {

//   @Value("${datajobs.security.kerberos.kerberosPrincipal}")
//   private String kerberosPrincipal;
//
//   @Value("${datajobs.security.kerberos.keytabFileLocation}")
//   private String keytabFileLocation;
//
//
//   @Override
//   protected void configure(HttpSecurity http) throws Exception {
//      http
//            .authorizeRequests()
//            .antMatchers("/**").authenticated()
//            .and()
//            .csrf().disable()
//            .addFilterBefore(
//                  spnegoAuthenticationProcessingFilter(authenticationManagerBean()),
//                  BasicAuthenticationFilter.class);
//   }
//
//   @Override
//   public void configure(WebSecurity web) {
//      web.ignoring().antMatchers(SecurityConfiguration.ENDPOINTS_TO_IGNORE);
//   }
//
//   @Override
//   protected void configure(AuthenticationManagerBuilder auth) {
//      auth.authenticationProvider(kerberosServiceAuthenticationProvider());
//
//   }
//
//   @Bean
//   public SpnegoAuthenticationProcessingFilter spnegoAuthenticationProcessingFilter(
//         AuthenticationManager authenticationManager) {
//      SpnegoAuthenticationProcessingFilter filter = new SpnegoAuthenticationProcessingFilter();
//      filter.setAuthenticationManager(authenticationManager);
//      return filter;
//   }
//
//   @Bean
//   public KerberosServiceAuthenticationProvider kerberosServiceAuthenticationProvider() {
//      KerberosServiceAuthenticationProvider provider = new KerberosServiceAuthenticationProvider();
//      provider.setTicketValidator(sunJaasKerberosTicketValidator());
//      provider.setUserDetailsService(dataJobsUserDetailsService());
//      return provider;
//   }
//
//   @Bean
//   public SunJaasKerberosTicketValidator sunJaasKerberosTicketValidator() {
//      SunJaasKerberosTicketValidator ticketValidator = new SunJaasKerberosTicketValidator();
//      ticketValidator.setServicePrincipal(kerberosPrincipal);
//      ticketValidator.setKeyTabLocation(new FileSystemResource(keytabFileLocation));
//      ticketValidator.setDebug(true);
//      return ticketValidator;
//   }
//
//   @Bean
//   public DataJobsUserDetailsService dataJobsUserDetailsService() {
//      return new DataJobsUserDetailsService();
//   }
//
//   @Override
//   @Bean
//   public AuthenticationManager authenticationManagerBean() throws Exception {
//      return super.authenticationManagerBean();
//   }
//
//   class DataJobsUserDetailsService implements UserDetailsService {
//
//      @Override
//      public UserDetails loadUserByUsername(String username) throws UsernameNotFoundException {
//         return new User(username, "", true, true, true, true, AuthorityUtils.createAuthorityList("ROLE_DATA_JOBS_USER"));
//      }
//
//   }
}
