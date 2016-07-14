core = { 
  "lti_version" : "LTI-1p0",
  "lti_message_type" : "basic-lti-launch-request",
  "resource_link_title" : "Activity: attend",
  "resource_link_description" : "A weekly blog.",
  "tool_consumer_info_product_family_code" : "ims",
  "tool_consumer_info_version" : "1.1",
  "tool_consumer_instance_guid" : "lmsng.ischool.edu",
  "tool_consumer_instance_description" : "University of Information",
  "launch_presentation_css_url" : "http://localhost:8888/tsugi/lms.css",
  "launch_presentation_return_url" : "http://lmsng.school.edu/portal/123/page/988/",
  "oauth_callback" : "about:blank"
}

# post1s
learner = { 
  "launch_presentation_css_url" : "http://localhost:8888/tsugi/lms.css",
  "context_label" : "SI106",
  "context_title" : "Introduction to Programming",
  "lis_person_name_full" : "John Student",
  "lis_person_contact_email_primary" : "john@ischool.edu",
  "lis_person_sourcedid" : "ischool.edu:john",
  "lis_result_sourcedid" : "99999999999999999999999999999999",
  "lis_outcome_service_url" : "http://localhost:8888/tsugi/common/tool_consumer_outcome.php?b64=MTIzNDU6OjpzZWNyZXQ6Ojo=",
  "roles" : "Learner" 
}


# post1 - A post from LTI 1.0
inst = { 
  "user_id" : "unittest:292832126",
  "context_id" : "unittest:456434513",
  "context_label" : "SI106",
  "context_title" : "Introduction to Programming",
  "lis_person_name_full" : "Jane Instructor",
  "lis_person_name_family" : "Instructor",
  "lis_person_name_given" : "Jane",
  "lis_person_contact_email_primary" : "inst@ischool.edu",
  "lis_person_sourcedid" : "ischool.edu:inst",
  "lis_result_sourcedid" : "e10e575674e68bbcd873e2962f5a138b",
  "lis_outcome_service_url" : "http://localhost:8888/tsugi/common/tool_consumer_outcome.php?b64=MTIzNDU6OjpzZWNyZXQ6Ojo=",
  "roles" : "Instructor" 
}

# post2 - A post that came through LTI 2.0
inst2 = { 
  "user_id" : "unittest:292832126",
  "resource_link_id" : "unittest:667587732",
  "resource_link_title" : "Activity: attend",
  "resource_link_description" : "A weekly blog.",
  "lti_message_type" : "basic-lti-launch-request",
  "custom_courseoffering_sourcedid" : "unittest:456434513",
  "custom_courseoffering_label" : "SI106",
  "custom_courseoffering_title" : "Introduction to Programming",
  "custom_person_name_full" : "Jane Instructor",
  "custom_person_name_family" : "Instructor",
  "custom_person_name_given" : "Jane",
  "custom_person_contact_email_primary" : "inst@ischool.edu",
  "custom_person_sourcedid" : "ischool.edu:inst",
  "custom_result_url" : "http://localhost:8888/tsugi/common/result.php?id=1234567",
  "custom_resourcelink_title" : "Activity: attend",
  "custom_resourcelink_description" : "A weekly blog.",
  "custom_result_comment" : "Nice work",
  "custom_result_resultscore" : "0.9",
  "custom_membership_role" : "Instructor" 
}
