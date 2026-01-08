#! C:\Perl\bin\perl.exe -I..\common

use strict;
use CGI;
use CGI::Carp qw(fatalsToBrowser);

use TMSstr;
use TMScommon;
use TMSlock;
use TMSselitem;

#require '../common/http_header.pm';

my $lang = &TMSstr::get_lang_set();
&TMSstr::load_str_file($lang);       # 必ず get_str() の前に実行する事！！

require 'shiftreport.pm';

my $menu_color = '#426AB3';
my $body_color = '#E1E2F2';

my $html = new CGI;

my $sel_mode = $html->param('sel_mode');

my %loom  = ();
my %style = ();
if( $sel_mode eq 'loom' ){
  my @p = $html->param('loom');
  if( $#p < 0 ){
    require '../common/http_header.pm';
    print &TMScommon::no_data_page( $menu_color, $body_color );
    exit;
  }
  foreach(@p){ $loom{$_} = 1; }
} else{
  my @p = $html->param('style');
  if( $#p < 0 ){
    require '../common/http_header.pm';
    print &TMScommon::no_data_page( $menu_color, $body_color );
    exit;
  }
  foreach(@p){ $style{$_} = 1; }
}


my $period = $html->param('period');  # 期間種類
my @shift  = $html->param('shift');
@shift = sort @shift;

my @file = ();
my @index = ();
&TMScommon::get_shift_file_list( $period, \@shift, \@file, \@index );
                                # @file:  期間(@shift)にマッチするファイル名
                                # @index: 期間(@shift)の表示用文字列

my $update_lock = '../../tmsdata/update.lock';
my $other_user;
if( &TMSlock::check_lockfile($update_lock,$ENV{REMOTE_ADDR},\$other_user) ){	# データ更新中は使用不可
    require '../common/http_header.pm';
  print &TMSlock::data_updating_page( $other_user );
  exit;
}

# 各ファイル名の取得
my $xlsfile  = "../xlsfile/$lang/shiftreport.xls";

my $datafile = &TMScommon::get_xlsdata_file_name("shiftreport","csv");

my $infofile = "shiftreport.tmshlp";


# ＣＳＶファイルの出力
my @val_item2     = &TMSselitem::get_value_of_item2();
my @val_item      = &TMSselitem::get_value_of_item();
my @val_item3     = &TMSselitem::get_value_of_item3();
my @val_detail    = &TMSselitem::get_value_of_detail();
my @val_color     = &TMSselitem::get_value_of_color();
my $val_beam_type = &TMSselitem::get_value_of_beam_type();
my $val_unit      = &TMSselitem::get_value_of_unit();

my @ttl_item2  = &TMSselitem::get_title_of_item2();
my @ttl_item   = &TMSselitem::get_title_of_item();
my @ttl_item3  = &TMSselitem::get_title_of_item3();
my @ttl_detail = &TMSselitem::get_title_of_detail();
my @ttl_color  = &TMSselitem::get_title_of_color();
my $ttl_unit   = &TMSselitem::get_title_of_unit();

my $jat_ari = &TMSselitem::is_jat_ari(),
my $lwt_ari = &TMSselitem::is_lwt_ari(),

my $jat_lwt_ari = (1==0); # False
if( ($jat_ari == 1) and ($lwt_ari == 1) ){ $jat_lwt_ari = (1==1); } # True


open(OUT, "> $datafile" );

my $now_date = &TMScommon::get_now_date();

print OUT	"( $now_date )\n".
		"$index[0] -> $index[$#index]\n".
		"\n";

print OUT &make_shiftreport_title( 'shift',
				   $period,
				   $sel_mode,
				   $jat_ari, $lwt_ari,
				   $val_beam_type,
				   $ttl_unit,
				   \@val_item2,  \@ttl_item2,
				   \@val_item,   \@ttl_item,
				   \@val_item3,  \@ttl_item3,
				   \@val_detail, \@ttl_detail,
				   \@val_color,  \@ttl_color  );

my $dcount = 0;
for( my $i=0; $i<=$#file; $i++ ){
  my $f = $file[$i];
  open(IN,"< $f");
  while(<IN>){
    my $line = $_;
    my $m = 0;
    if( $sel_mode eq "loom" ){
      if( $line =~ m/,mac_name ([^,]+)/ ){
        if( exists($loom{$1}) ){ $m = 1; }
      }
    } else{  # "style"
      if( $line =~ m/,style ([^,]+)/ ){
        if( exists($style{$1}) ){ $m = 1; }
      }
    }
    if( $m ){

      $dcount++;
      print OUT &make_shiftreport_data( 'shift',
					$index[$i],
					$sel_mode,
					\$line,
					$jat_lwt_ari,
					$val_beam_type,
					$val_unit,
					\@val_item2,
					\@val_item,
					\@val_item3,
					\@val_detail,
					\@val_color  );

    }
  }
  close(IN);
}
close(OUT);


if( $dcount == 0 ){
  require '../common/http_header.pm';
  print &TMScommon::no_data_page( $menu_color, $body_color );
}
else{
  # TmsHelper.exe 用情報データ出力
  &TMScommon::http_header_tmsinf($infofile);

  print "method POPUP_EXCEL\n";
  print "version 1.0\n";

  print "xlsfile ". &TMScommon::get_fullpath_url($xlsfile). "\n";

  if( $ENV{REMOTE_ADDR} eq '127.0.0.1' ){  # ローカルの場合（データ読み込み高速化の為）
    print "csvfile1 ". &TMScommon::get_fullpath_file($datafile). "\n";
  }else{  # リモートの場合
    print "csvfile1 ". &TMScommon::get_fullpath_url($datafile). "\n";
  }

  #print "macro start_make_all\n";
}

