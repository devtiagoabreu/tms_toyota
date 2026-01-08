#! C:\Perl\bin\perl.exe -I..\common

use strict;
use CGI;
use CGI::Carp qw(fatalsToBrowser);

use TMSstr;
use TMScommon;
use TMSdeny;
use TMSscanner;

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

#######################################################################

my $html = new CGI;

my $err1 = 1;
my $passwd1_on = $html->param('passwd1_on');
if( $passwd1_on ){
  my $passwd1a = $html->param('passwd1a');
  my $passwd1b = $html->param('passwd1b');

  if( $passwd1a eq $passwd1b ){
    
    open(PIPE,"..\\..\\..\\bin\\htpasswd.exe -nbm TMS $passwd1a | ");
    my @result = <PIPE>;
    close(PIPE);

    foreach(@result){
      if( m/^TMS:/ ){
        $err1 = 0;

	chomp;
	my @passwd = ($_);
	my @htaccess =	( "AuthType Basic",
			  "AuthName \"Toyota Monitoring System\"",
			  "AuthUserFile htdocs/TmsScanner/passwd/scanloom_passwd.txt",
			  "require valid-user" );

	&TMSscanner::upload_scanner_file( 1,  # スキャナー１のみ
                                          ["passwd/scanloom_passwd.txt","passwd/scanloom/.htaccess"],
                                          \@passwd,                     \@htaccess );

        last;
      }
    }
  }
}
else{ # Disable Password
  $err1 = 0;
  # データ無しを送って、ファイル削除する

  &TMSscanner::upload_scanner_file( 1,  # スキャナー１のみ
                                    ["passwd/scanloom_passwd.txt","passwd/scanloom/.htaccess"],
                                    [],                           [] );
}
#######################################################################

my $err2 = 1;
my $passwd2_on = $html->param('passwd2_on');
if( $passwd2_on ){
  my $passwd2a = $html->param('passwd2a');
  my $passwd2b = $html->param('passwd2b');

  if( $passwd2a eq $passwd2b ){

    open(PIPE,"..\\..\\..\\bin\\htpasswd.exe -nbm TMS $passwd2a | ");
    my @result = <PIPE>;
    close(PIPE);

    foreach(@result){
      if( m/^TMS:/ ){
        $err2 = 0;

	chomp;
	my @passwd = ($_);
	my @htaccess =	( "AuthType Basic",
			  "AuthName \"Toyota Monitoring System\"",
			  "AuthUserFile htdocs/TmsScanner/passwd/scanset_passwd.txt",
			  "require valid-user" );

	&TMSscanner::upload_scanner_file( 1,  # スキャナー１のみ
                                          ["passwd/scanset_passwd.txt","passwd/scanset/.htaccess"],
                                          \@passwd,                    \@htaccess );

        last;
      }
    }
  }
}
else{ # Disable Password
  $err2 = 0;
  # データ無しを送って、ファイル削除する

  &TMSscanner::upload_scanner_file( 1,  # スキャナー１のみ
                                    ["passwd/scanset_passwd.txt","passwd/scanset/.htaccess"],
                                    [],                          [] );
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

if( $err1 or $err2 ){
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

