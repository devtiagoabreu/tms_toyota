#! C:\Perl\bin\perl.exe -I..\common

use strict;
use CGI;
use CGI::Carp qw(fatalsToBrowser);

use TMSstr;
use TMScommon;
use TMSscanner;

require '../common/http_header.pm';

my $lang = &TMSstr::get_lang_set();
&TMSstr::load_str_file($lang);       # 必ず get_str() の前に実行する事！！

my $str_SETTING_RESULT		= &TMSstr::get_str( "SETTING_RESULT"	);
my $str_SETTING_SUCCEED		= &TMSstr::get_str( "SETTING_SUCCEED"	);
my $str_MENU			= &TMSstr::get_str( "MENU"		);
my $str_BACK			= &TMSstr::get_str( "BACK"		);

#######################################################

my $html = new CGI;

my $length_unit  = $html->param('length_unit');
my $density_unit = $html->param('density_unit');

my @unit_set = ();

my @len_val = ("pick","meter","yard");
push(@unit_set,"length_unit $len_val[$length_unit]");

my @den_val = ("cm","inch");
push(@unit_set,"density_unit $den_val[$density_unit]");


# 変更前の設定値を読み込み
my @system_set_old = &TMSscanner::get_system_set();

# 変更後の設定ファイルを作成
my @system_set_new = ();
foreach(@system_set_old){
  if   ( m/^length_unit /  ){ next; }
  elsif( m/^density_unit / ){ next; }

  push(@system_set_new,$_);
}

push(@system_set_new,@unit_set);


# 設定ファイルをスキャナーに転送

&TMSscanner::upload_scanner_file( "all",
                                  ["set/system_set.txt","set/system_set.update"],
                                  \@system_set_new,     ["update"] );


## 画面表示 ########################################

my $tbl_width = 630;
my $title = $str_SETTING_RESULT;
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

  print	"<font size=+2><B>$str_SETTING_SUCCEED</B></font>\n";

print	"<BR><BR><BR>\n".
	"<NOBR>\n".
	"<A HREF=\"../\"><IMG SRC=\"../image/menu2_$lang.jpg\" width=85 height=27 alt=\"$str_MENU\" border=0></A>\n".
	"<A HREF=\"unitset.cgi\"><IMG SRC=\"../image/back2_$lang.jpg\" width=85 height=27 alt=\"$str_BACK\" border=0></A>\n".
	"</NOBR>\n".
	"<BR><BR><BR><BR>\n".
	"</td></tr>\n".
	"</table><BR>\n".

	&TMScommon::make_footer('dummy','menu', $lang).
	"</center></body></html>\n";

