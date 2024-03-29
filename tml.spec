Summary:	Mailing list manager written in Ruby
Summary(pl.UTF-8):	Zarządca list dyskusyjnych napisany w języku Ruby
Name:		tml
Version:	0.5.1
Release:	1
License:	GPL
Group:		Applications/Mail
Source0:	http://www.tmtm.org/ja/ruby/tml/%{name}-%{version}.tar.gz
# Source0-md5:	fc6b32f55999c0d7887c386842a6092d
Patch0:		%{name}-paths.patch
URL:		http://www.tmtm.org/ja/ruby/tml/
BuildRequires:	rpmbuild(macros) >= 1.277
BuildRequires:	ruby-devel
Requires(post):	fileutils
Requires(post):	grep
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
%{?ruby_mod_ver_requires_eq}
Requires:	ruby-mysql
Provides:	group(tml)
Provides:	user(tml)
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Mailing list manager written in Ruby.

%description -l pl.UTF-8
Zarządca list dyskusyjnych napisany w języku Ruby.

%prep
%setup -q
%patch0 -p1

%build

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_localstatedir}/spool/tml,%{_sbindir},%{_libdir}/%{name}/templates,%{ruby_rubylibdir}/%{name},%{_localstatedir}/spool/%{name},/etc/mail}

install tmladmin $RPM_BUILD_ROOT%{_sbindir}
install tml tmlctl $RPM_BUILD_ROOT%{_libdir}/%{name}
install tml.rb mail.rb tml-file.rb tml-mysql.rb $RPM_BUILD_ROOT%{ruby_rubylibdir}/%{name}
install templates/* $RPM_BUILD_ROOT%{_libdir}/%{name}/templates
echo '$domain = "localdomain"' > $RPM_BUILD_ROOT/etc/mail/tml.conf

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -f -g 132 -r tml
%useradd -u 132 -r -d %{_localstatedir}/spool/tml -s /bin/false -c "TML Mailing list manager" -g tml tml

%postun
if [ "$1" = "0" ]; then
	%userremove %{name}
	%groupremove %{name}
fi

%post
# alias:
umask 022
if [ -f /etc/mail/aliases ]; then
	if [ -e /etc/smrsh ]; then
		if ! grep -q "^%{name}:" /etc/mail/aliases; then
			echo "%{name}:  \"|/etc/smrsh/tml\"" >> /etc/mail/aliases
			newaliases || :
		fi
	else
		if ! grep -q "^%{name}:" /etc/mail/aliases; then
			echo "%{name}:  \"|%{_libdir}/%{name}/%{name}\"" >> /etc/mail/aliases
			newaliases || :
		fi
	fi
fi

# mailname:
if [ ! -f /etc/mail/mailname -a -d /etc/mail -a -x /bin/hostname ]; then
	hostname -f > /etc/mail/mailname
fi

# Detect SMRSH
if [ -e /etc/smrsh -a ! -e /etc/smrsh/tml ]; then
	echo "#!/bin/sh" > /etc/smrsh/tml
	echo "%{_bindir}/tml \$@" >> /etc/smrsh/tml
	chmod ug+rx /etc/smrsh/tml

	echo "Your installation has been detected to have SMRSH, the SendMail"
	echo "Restricted SHell, installed. If this is your first install, you"
	echo "will want to change the address for TML in the aliases file to be"
	echo "/etc/smrsh/tml instead of /usr/bin/tml"
	chmod a+x /etc/smrsh/tml
fi

%files
%defattr(644,root,root,755)
%doc README.html tommy.css mysql.sql
%config(noreplace) /etc/mail/tml.conf
%dir %{_libdir}/%{name}
%dir %{_libdir}/%{name}/templates
%{_libdir}/%{name}/templates/*
%attr(755,root,root) %{_libdir}/%{name}/tml
%attr(755,root,root) %{_libdir}/%{name}/tmlctl
%attr(755,root,root) %{_sbindir}/tmladmin
%{ruby_rubylibdir}/%{name}
%attr(755,tml,tml) %{_localstatedir}/spool/tml
