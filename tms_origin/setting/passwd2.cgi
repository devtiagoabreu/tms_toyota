#! C:\Perl\bin\perl.exe -I..\common

use strict;
use CGI;
use CGI::Carp qw(fatalsToBrowser);

use TMSstr;
use TMScommon;
use TMSdeny;

require '../common/http_header.pm';

my $lang = &TMSstr::get_lang_set();
&TMSstr::load_str_file($lang);       # 必ず get_str() の前に実行する事！！

my $str_SETTING_RESULT		= &TMSstr::get_str( "SETTING_RESULT"	);
my $str_PASSWORD_ERROR		= &TMSstr::get_str( "PASSWORD_ERROR"	);
my $str_SETTING_SUCCEED		= &TMSstr::get_str( "SETTING_SUCCEED"	);
my $str_MENU			= &TMSstr::get_str( "MENU"		);
my $str_BACK			= &TMSstr::get_str( "BACK"		);

if( $ENV{REMOTE_ADDR} ne '127.0.0.1' ){
  print &TMSdeny::permission_deny_page();
  exit;
}

my $passwd_dir  = 'setting';
my $passwd_file = 'passwd.txt';

my $htaccess =	"AuthType Basic\n".
		"AuthName \"Toyota Monitoring System\"\n".
		"AuthUserFile htdocs/tmsdata/$passwd_dir/$passwd_file\n".
	#	"AuthGroupFile htdocs/tmsdata/setting/group.txt\n".
		"require valid-user\n";

my $html = new CGI;

my $err = 1;
my $passwd_on = $html->param('passwd_on');
if( $passwd_on ){
  my $passwd1 = $html->param('passwd1');
  my $passwd2 = $html->param('passwd2');

  if( $passwd1 eq $passwd2 ){
    
    open(PIPE,"..\\..\\..\\bin\\htpasswd.exe -nbm TMS $passwd1 | ");
    my @result = <PIPE>;
    close(PIPE);

    foreach(@result){
      if( m/^TMS:/ ){
        $err = 0;

        &TMScommon::make_dir( '../../tmsdata' );
        &TMScommon::make_dir( "../../tmsdata/$passwd_dir" );

        open(PASS,"> ../../tmsdata/$passwd_dir/$passwd_file" );
        print PASS $_;
        close(PASS);

        open(HTAC,'> .htaccess');		# Setting
        print HTAC $htaccess;
        close(HTAC);

        open(HTAC,'> ../loom/.htaccess');	# Loom Data
        print HTAC $htaccess;
        close(HTAC);

        open(HTAC,'> ../edit/.htaccess');	# Data Edit
        print HTAC $htaccess;
        close(HTAC);

        last;
      }
    }
  }
}
else{ # Disable Password
  $err = 0;
  if( -f '.htaccess' ){ unlink('.htaccess'); }			# Setting
  if( -f '../loom/.htaccess' ){ unlink('../loom/.htaccess'); }	# Loom Data
  if( -f '../edit/.htaccess' ){ unlink('../edit/.htaccess'); }	# Data Edit
}

my $tbl_width = 630;
my $menu_color = '#ED1C24';
my $body_color = '#FDE1D4';

my $title = $str_SETTING_RESULT;

print	"<html lang=$lang>\n".
	"<head>\n".
	&TMScommon::meta_content_type( $lang ).
	&TMScommon::meta_no_cache_tag().
	"<title>$title</title>\n".
	"</head>\n".
	"<body bgcolor=#C7C4E2><center>\n".
	&TMScommon::make_header('menu','dummy', $lang)."<BR>".

	"<table border=1 frame=box width=$tbl_width cellPadding=6>\n".
	"<tr align=center bgcolor=$menu_color>\n".
	"<th><font size=+2 color=white>$title</font></th>\n".
	"</tr>\n".
	"<tr align=center bgcolor=$body_color><td>\n".
	"<BR><BR><BR>\n";

if( $err ){
  print	"<font size=+2><B>$str_PASSWORD_ERROR</B></font>\n";
} else{
  print	"<font size=+2><B>$str_SETTING_SUCCEED</B></font>\n";
}
print	"<BR><BR><BR>\n".
	"<NOBR>\n".
	"<A HREF=\"../\"><IMG SRC=\"../image/menu2_$lang.jpg\" width=85 height=27 alt=\"$str_MENU\" border=0></A>\n".
	"<A HREF=\"passwd.cgi\"><IMG SRC=\"../image/back2_$lang.jpg\" width=85 height=27 alt=\"$str_BACK\" border=0></A>\n".
	"</NOBR>\n".
	"<BR><BR><BR><BR>\n".
	"</td></tr>\n".
	"</table><BR>\n".

	&TMScommon::make_footer('dummy','menu', $lang).
	"</center></body></html>\n";

