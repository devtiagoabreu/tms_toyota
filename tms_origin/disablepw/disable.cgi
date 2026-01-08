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

my $str_DISABLE_PASSWORD_FORCIBLY	= &TMSstr::get_str( "DISABLE_PASSWORD_FORCIBLY"	);
my $str_PASSWORD_IS_DISABLED		= &TMSstr::get_str( "PASSWORD_IS_DISABLED"	);
my $str_MENU				= &TMSstr::get_str( "MENU"			);

if( $ENV{REMOTE_ADDR} ne '127.0.0.1' ){
  print &TMSdeny::permission_deny_page();
  exit;
}

# パスワードをかけるディレクトリ一覧を取得
my @security_dir = ();
if( open(FILE, "< ..\\security_dir.txt") ){
  while(<FILE>){
    chomp;
    my ($user,$dir) = split(/,/);
    if( defined($dir) ){
      push(@security_dir, $dir);
    }
  }
}
# 対象ディレクトリに .htaccess が存在したら消す
foreach my $dir (@security_dir){
  my $fname = "..\\$dir\\.htaccess";
  if( -f $fname ){ unlink( $fname ); }
}


my $title = $str_DISABLE_PASSWORD_FORCIBLY;

my $tbl_width = 630;
my $menu_color = '#ED1C24';
my $body_color = '#FDE1D4';

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

print	"<font size=+2><B>$str_PASSWORD_IS_DISABLED</B></font>\n";

print	"<BR><BR><BR>\n".
	"<NOBR>\n".
	"<A HREF=\"../\"><IMG SRC=\"../image/menu2_$lang.jpg\" width=85 height=27 alt=\"$str_MENU\" border=0></A>\n".
	"</NOBR>\n".
	"<BR><BR><BR><BR>\n".
	"</td></tr>\n".
	"</table><BR>\n".

	&TMScommon::make_footer('dummy','menu', $lang).
	"</center></body></html>\n";

