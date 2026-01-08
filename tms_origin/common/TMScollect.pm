package TMScollect;

###################################################################################################
#
# TMScollect.pm
#
###################################################################################################

use strict;

use TMSstr;
use TMScommon;
use TMSselitem;

###################################################################################################

sub need_collection_page
{
  my ( $url) = @_;

  my $lang = &TMSstr::get_lang();

  my $tbl_width = 630;
  my $menu_color = '#FDB913';
  my $body_color = '#FFF2DD';

  my $title = &TMSstr::get_str("DATA_IS_NOT_COLLECTED_FOR_A_WHILE");
  my $submit_button = &TMSstr::get_str("MOVE_TO_DATA_COLLECTION");
  my $cgifile = '../loom/getdata.cgi';

  my $html = 	"<html lang=$lang>\n".
		"<head>\n".
		"<STYLE TYPE=\"text/css\">\n".
		"A:link    { color: Midnightblue }\n".
		"A:visited { color: Midnightblue }\n".
		"A:active  { color: Red }\n".
		"</STYLE>\n".
		&TMScommon::meta_content_type( $lang ).
		&TMScommon::meta_no_cache_tag().
		"<title>$title</title>\n".
		"<script language=JavaScript>\n".
		"<!--\n".
		"  var submit_disflg = 0;\n".
		"  function disable_submit() {\n".
		"    document.fminput.submit.disabled = true;\n".
		"    if(submit_disflg==0){\n".
		"      submit_disflg = 1;\n".
		"      return true;\n".
		"    }else{\n".
		"      return false;\n".
		"    }\n".
		"  }\n".
		"//-->\n".
		"</script>\n".
		"</head>\n".
		"<body bgcolor=#C7C4E2><center>\n".
		&TMScommon::make_header('menu','dummy', $lang)."<BR>".

		"<table border=1 frame=box width=$tbl_width cellPadding=6>\n".
		"<tr align=center bgcolor=$menu_color>\n".
		"<th><font size=+2 color=white>$title</font></th>\n".
		"</tr>\n".
		"<tr align=center bgcolor=$body_color><td>\n".
		"<BR><BR><BR>\n".
		"<font size=+1><B>".&TMSstr::get_str("IS_DATA_COLLECTED_FIRST")."</B></font>\n".
		"<BR><BR><BR><BR>\n".
		"<B>\n".
		"<A HREF=$url>&lt&nbsp;".&TMSstr::get_str("KEEP_GOING")."&nbsp;&gt</A>&nbsp;&nbsp;&nbsp;&nbsp;".
		"<A HREF=\"javascript:history.back()\">&lt&nbsp;".&TMSstr::get_str("BACK")."&nbsp;&gt</A>\n".
		"</B>\n".
		"<BR><BR><BR>\n".

		"<form name=\"fminput\" action=\"$cgifile\" method=POST onSubmit=\"return disable_submit()\">\n".
		"<input type=SUBMIT name=\"submit\" value=\"$submit_button\">\n".
		"<BR><BR></form>\n".

		"</td></tr>\n".
		"</table><BR>\n".

		&TMScommon::make_footer('dummy','menu', $lang).
		"</center></body></html>\n";
  return $html;
}

###################################################################################################

my $datefile = "..\\..\\tmsdata\\collect_date.txt";

sub check_collect_date
{
  if( ( ! -f "..\\..\\tmsdata\\setting\\ipaddress.txt" ) and
      ( ! -f "..\\..\\tmsdata\\setting\\scanner_ip.txt" ) ){
    return 0;  # IP設定されてなければ、チェックしない
  }

  if( -f $datefile ){
    if( open(DATE,"< $datefile") ){
      my $last_date = <DATE>;  # 最後の収集時間（または、猶予時間）
      close(DATE);

      my $now = time();  # 現在時間
      my $pass_time = 0;
      if( $now >= $last_date ){
        $pass_time = $now - $last_date;  # 経過時間
      }
      #else{  # 保存時刻が未来なら、現在の時刻で上書きする
      #  &update_collect_date(); 
      #}

      my $expire = &TMSselitem::get_value_of_expire();
      if( $pass_time < ($expire * 3600) ){ return 0; }
    }
  }
  return 1;
}

#------------------------------------------------------------

sub extend_1hour
{
  if( open(DATE,"> $datefile") ){
    my $now = time();
    my $expire = &TMSselitem::get_value_of_expire();
    print DATE ($now - (($expire - 1) * 3600));  # １時間後に期限が来る様に設定
    close(DATE);
  }
}

#------------------------------------------------------------

sub update_collect_date
{
  if( open(DATE,"> $datefile") ){
    my $now = time();
    print DATE $now;  # 現在時刻を保存
    close(DATE);
  }
}

###################################################################################################
1;
