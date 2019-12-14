Name:          log4j12
Version:       1.2.17
Release:       24
Summary:       A logging library for Java
License:       ASL 2.0
URL:           http://logging.apache.org/log4j/1.2/
BuildArch:     noarch
Source0:       https://github.com/apache/log4j/archive/v1_2_17.tar.gz
Source1:       log4j.catalog

Patch0000:     0001-logfactor5-changed-userdir.patch
Patch0001:     0009-Fix-tests.patch
Patch0002:     0010-Fix-javadoc-link.patch
Patch0003:     0001-Backport-fix-for-CVE-2017-5645.patch

BuildRequires: maven-local mvn(ant-contrib:ant-contrib) mvn(javax.mail:mail)
BuildRequires: mvn(junit:junit) mvn(org.apache.ant:ant-junit)
BuildRequires: mvn(org.apache.felix:maven-bundle-plugin)
BuildRequires: mvn(org.apache.geronimo.specs:geronimo-jms_1.1_spec)
BuildRequires: mvn(org.apache.maven.plugins:maven-antrun-plugin)
BuildRequires: mvn(org.apache.maven.plugins:maven-assembly-plugin)
BuildRequires: mvn(oro:oro) mvn(org.apache.ant:ant-nodeps)

Obsoletes:     log4j <= 0:1.2.17-14

%description
With log4j it is possible to enable logging at runtime
without modifying the application binary.

%package help
Summary:       Help for log4j12
Provides:      log4j12-doc = %{version}-%{release}
Obsoletes:     log4j12-doc < %{version}-%{release}

%description help
This package contains help for log4j12.

%prep
%autosetup -n log4j-1_2_17 -p1

find . \( -name "*.jar" -o -name "*.class" -o -name "*.dll" \) -exec rm -f {} \;
rm -rf docs/api

%pom_remove_plugin :clirr-maven-plugin
%pom_remove_plugin :maven-site-plugin
%pom_remove_plugin :maven-source-plugin
%pom_remove_plugin :rat-maven-plugin
%pom_xpath_remove "pom:build/pom:plugins/pom:plugin[pom:artifactId = 'maven-javadoc-plugin']/pom:executions"

%pom_remove_dep org.apache.openejb:javaee-api

sed -i.ant "s|groupId>ant<|groupId>org.apache.ant<|g" pom.xml

sed -i.javac "s|1.4|1.6|g" pom.xml build.xml
sed -i.javac "s|1.1|1.6|g" tests/build.xml

sed -i.javax.jmdns "s|javax.jmdns.*;resolution:=optional,|!javax.jmdns.*,|g" pom.xml
%pom_xpath_inject "pom:build/pom:plugins/pom:plugin[pom:artifactId = 'maven-bundle-plugin']/pom:configuration/pom:instructions" "
  <Bundle-SymbolicName>org.apache.log4j</Bundle-SymbolicName>
  <_nouses>true</_nouses>"

%pom_xpath_remove "pom:build/pom:plugins/pom:plugin[pom:artifactId = 'maven-antrun-plugin']/pom:executions/pom:execution[pom:phase = 'process-classes' ]"

%pom_xpath_set "pom:plugin[pom:artifactId='maven-assembly-plugin']/pom:executions/pom:execution/pom:goals/pom:goal[text()='assembly']" single

install -d tests/lib/

cd tests/lib/
ln -s `build-classpath jakarta-oro`
ln -s `build-classpath javamail/mail`
ln -s `build-classpath junit`
cd -

%mvn_compat_version log4j:log4j 1.2.17 1.2.16 1.2.15 1.2.14 1.2.13 1.2.12 12
rm -r src/main/java/org/apache/log4j/nt/NTEventLogAppender.java tests/src/java/org/apache/log4j/nt/NTEventLogAppenderTest.java

find tests/src/java/org/apache/log4j/net/TelnetAppenderTest.java -delete
sed -i '/TelnetAppenderTest/d' tests/src/java/org/apache/log4j/CoreTestSuite.java

%mvn_file log4j:log4j log4j %{name}

%build
%mvn_build

%install
%mvn_install -X

ln -s log4j-%{version}.jar %{buildroot}%{_javadir}/log4j-1.jar

install -pD -T -m 644 src/main/javadoc/org/apache/log4j/xml/doc-files/log4j.dtd %{buildroot}%{_datadir}/sgml/log4j/log4j.dtd
install -pD -T -m 644 %{SOURCE1} %{buildroot}%{_datadir}/sgml/log4j/catalog

%post
if [ -x %{_bindir}/install-catalog -a -d %{_sysconfdir}/sgml ]; then
  %{_bindir}/install-catalog --add %{_sysconfdir}/sgml/log4j-%{version}-%{release}.cat %{_datadir}/sgml/log4j/catalog > /dev/null || :
fi
if [ -x %{_bindir}/xmlcatalog -a -w %{_sysconfdir}/xml/catalog ]; then
  %{_bindir}/xmlcatalog --noout --add public "-//APACHE//DTD LOG4J 1.2//EN" file://%{_datadir}/sgml/log4j/log4j.dtd %{_sysconfdir}/xml/catalog > /dev/null
  %{_bindir}/xmlcatalog --noout --add system log4j.dtd file://%{_datadir}/sgml/log4j/log4j.dtd %{_sysconfdir}/xml/catalog > /dev/null || :
fi

%preun
if [ $1 -eq 0 ]; then
  if [ -x %{_bindir}/xmlcatalog -a -w %{_sysconfdir}/xml/catalog ]; then
    %{_bindir}/xmlcatalog --noout --del file://%{_datadir}/sgml/log4j/log4j.dtd %{_sysconfdir}/xml/catalog > /dev/null || :
  fi
fi

%postun
if [ -x %{_bindir}/install-catalog -a -d %{_sysconfdir}/sgml ]; then
  %{_bindir}/install-catalog --remove %{_sysconfdir}/sgml/log4j-%{version}-%{release}.cat %{_datadir}/sgml/log4j/catalog > /dev/null || :
fi

%files -f .mfiles
%{_javadir}/log4j-1.jar
%{_datadir}/sgml/log4j
%license LICENSE NOTICE

%files help -f .mfiles-javadoc

%changelog
* Fri Dec 13 2019 openEuler Buildteam <buildteam@openeuler.org> - 1.2.17-24
- Package init
