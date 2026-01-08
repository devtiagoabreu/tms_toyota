#! C:\Perl\bin\perl.exe -I..\common

use strict;
use CGI;
use CGI::Carp qw(fatalsToBrowser);

use TMSstr;
use TMScommon;
use TMSipset;
use TMSscanner;

require '../common/http_header.pm';

my $lang = &TMSstr::get_lang_set();
&TMSstr::load_str_file($lang);       # 必ず get_str() の前に実行する事！！

my $str_DATA_COLLECTION_NETWORK	= &TMSstr::get_str( "DATA_COLLECTION_NETWORK"	);
my $str_SELECT_ALL		= &TMSstr::get_str( "SELECT_ALL"		);
my $str_ENTER			= &TMSstr::get_str( "ENTER"			);

## システム全体の、機台ID・機台名のリストを取得
my @loom_id_name = &get_loom_id_name_list();

## 機台名、機台ID順にソート
@loom_id_name = sort { "$$a[1] $$a[0]" cmp "$$b[1] $$b[0]" } @loom_id_name;


################################################################

my $tbl_width = 630;
my $menu_color = '#FDB913';
my $body_color = '#FFF2DD';

my $cgifile = 'getdata2.cgi';
my $title = $str_DATA_COLLECTION_NETWORK;
my $submit_button = $str_ENTER;

print	"<html lang=$lang>\n".
	"<head>\n".
	&TMScommon::meta_content_type( $lang ).
	&TMScommon::meta_no_cache_tag().
	"<title>$title</title>\n".
	"<script language=JavaScript>\n".
	"<!--\n".
	"  function sel_loom() {\n".
	"    document.fminput.all_loom.checked = false;\n".
	"  }\n".
	"  function sel_all_loom() {\n".
	"    len = document.fminput.loom.length;\n".
	"    val = document.fminput.all_loom.checked;\n".
	"    for (i = 0; i < len; i++) {\n".
	"      document.fminput.loom.options[i].selected = val;\n".
	"    }\n".
	"  }\n".
	"//-->\n".
	"</script>\n".
	"</head>\n".
	"<body bgcolor=#C7C4E2><center>\n".
	&TMScommon::make_header('menu','dummy', $lang)."<BR>\n".

	"<form name=\"fminput\" action=\"$cgifile\" method=POST>\n".

	"<table border=1 frame=box width=$tbl_width cellPadding=6>\n".
	"<tr align=center bgcolor=$menu_color>\n".
	"<th><font size=+2 color=white>$title</font></th>\n".
	"</tr>\n".

	"<tr align=center bgcolor=$body_color>\n".
	"<td><select name=\"loom\" size=18 multiple onFocus=\"sel_loom()\">\n";

foreach( @loom_id_name ){
  if( $$_[0] eq $$_[1] ){
    print "<option value=\"$$_[0] $$_[1]\">$$_[1]</option>\n";
  }else{
    print "<option value=\"$$_[0] $$_[1]\">$$_[1] ($$_[0])</option>\n";
  }
}


print	"</select><br>\n".
	"<input type=CHECKBOX name=\"all_loom\" OnClick=\"sel_all_loom()\"><font size=+1><B>$str_SELECT_ALL</B></font>\n".
	"</td></tr>\n".
	"<tr><td align=center bgcolor=$body_color>\n".
	"<input type=SUBMIT name=\"submit\" value=\"$submit_button\">\n".
	"</td></tr>\n".
	"</table>\n".
	"<BR></form>\n".

	&TMScommon::make_footer('dummy','menu', $lang).
	"</center></body></html>\n";


########################################################################

sub get_loom_id_name_list
{

  # スキャナーの機台を登録
  my @loom_set = &TMSscanner::get_loom_setting( "mac_name" );
  foreach(@loom_set){
    # 機台名が未設定の場合は、機台IDで表示
    if( length($$_[1]) == 0 ){ $$_[1] = $$_[0]; }
  }

  # JAT710の機台を登録
  my @ip_list = &TMSipset::get_all_ip_list();
  if( $#ip_list >= 0 ){
    my @name_list = ();
    &TMSipset::get_name_ip_list( \@name_list, \@ip_list );
    for( my $i=0; $i<=$#name_list; $i++ ){
      push( @loom_set, [$ip_list[$i], $name_list[$i]] );
    }
  }

  return @loom_set;  # ソートはしない
}

########################################################################
