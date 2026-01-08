#! C:\Perl\bin\perl.exe -I..\common

use strict;
use CGI;
use CGI::Carp qw(fatalsToBrowser);


use TMSstr;
use TMScommon;
use TMSlock;

#require '../common/http_header.pm';

my $lang = &TMSstr::get_lang_set();
&TMSstr::load_str_file($lang);       # 必ず get_str() の前に実行する事！！

### 履歴元フォルダのパスを設定 ###
my $stophistory_dir = "..\\..\\tmsdata\\stop_history";

&main();

#####################################################################
sub main{
  my $menu_color = '#426AB3';
  my $body_color = '#E1E2F2';

  ### レポート対象取得 ###
  my $html = new CGI;

  my @date_list = $html->param('date');
  my $loom      = $html->param('loom');

  ### 履歴データファイル名の取得 ###
  @date_list = sort @date_list;
  my @file_list = &get_stophistory_file_list( \@date_list, $loom );
  if( $#file_list < 0 ){
    # 該当する停台履歴が存在しなければ終了
    require '../common/http_header.pm';
    print &TMScommon::no_data_page( $menu_color, $body_color );
    exit;
  }
 
  ### ロックファイル ###
  my $update_lock = '../../tmsdata/update.lock';
  my $other_user;
  if( &TMSlock::check_lockfile($update_lock,$ENV{REMOTE_ADDR},\$other_user) ){	# データ更新中は使用不可
    require '../common/http_header.pm';
    print &TMSlock::data_updating_page( $other_user );
    exit;
  }
  
  # 各ファイル名の取得
  my $xlsfile = "../xlsfile/$lang/stophistory.xls";

  my $datafile = &TMScommon::get_xlsdata_file_name("stophistory","csv");

  my $infofile = "stophistory.tmshlp";


  # ＣＳＶファイルの出力
  &TMSstr::load_stop_cause();  # 停止原因文字列の読込

  open(OUT, "> $datafile" );

  # ヘッダー部
  my $now_date = &TMScommon::get_now_date();

  my $priod_start = $date_list[0];
  my $priod_end   = $date_list[$#date_list];
  $priod_start =~ s/\./\//g; # 2005.06.03 -> 2005/06/03
  $priod_end   =~ s/\./\//g;

  print OUT "( $now_date )\n".
            "$priod_start -> $priod_end\n".
            "$loom\n".
            "\n";

  # 項目
  print OUT "ORDER,DATE,STOP_TIME_POINT,RUN_TIME_POINT,DUMMY,STOP_CAUSE\n";

  # 履歴データ
  my $dcount = 0;
  foreach my $data_file ( @file_list ){

    # 履歴データファイルを開く
    if( open(HIST, "< $data_file") ){

      # 一行目
      my $line = <HIST>;
      chomp $line;  # 改行を削除

      # day, mac_type の値を取得する
      my $day = "";
      my $mac_type = "JAT710";  # デフォルト(古いデータで値無しの場合)

      my @item = split(/,/, $line);  # ,(カンマ) 区切り
      foreach( @item ){
        my @col = split(/ /, $_, 2); # スペース区切り
        if( $#col >= 1 ){  # 値があれば
          if( $col[0] eq 'day' ){
            $day = $col[1];  # yyyy.mm.dd
            if( $day =~ m/^\d{4}\.\d{2}\.\d{2}$/ )
                { $day =~ s/\./\//g; }  # 2005.06.03 -> 2005/06/03
            else{ $day = ""; }
          }
          elsif( $col[0] eq 'mac_type' ){
            $mac_type = $col[1];
          }
        }
      }

      if( $day ne "" ){
        ### 2行目以降を処理 ###
        while( $line = <HIST> ){
          chomp $line;  # 改行を削除
          if( length($line) <= 0 ){ next; } # データが無ければスキップ

          ### 停止時刻、運転時刻、停止原因番号 に分解 ###
          my ($stop_time, $run_time, $code) = split( /,/ , $line );
          if( ! defined($code) ){ $code = ""; }

          ### 行を出力 ###
          print OUT ++$dcount.  ",".   # 番号
                    $day.       ",".   # 日付
                    $stop_time. ",".   # 停止時刻
                    $run_time.  ",";   # 運転時刻

          if( $code ne "" ){ print OUT '="['.$code.']",'; }  # 停止原因コード
          else{              print OUT '="[----]",';      }

          print OUT '="'.&TMSstr::get_stop_cause($code,$mac_type).'"'. "\n";  # 停止原因
        }
      }
      close(HIST);
    }
  }
  close(OUT);


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

#####################################################################
#
# 引数 : $r_date 対象日の配列の参照
#        $loom   対象機台
#
# 戻り値 : ファイル名の配列
#

sub get_stophistory_file_list
{
  my ( $r_date, $loom ) = @_;

  my @file_list = ();

  # 日付ごとに
  foreach my $date ( @$r_date){

    # indexファイルを読み、機台名から履歴データファイル名を探す
    if( open(INDEX, "< $stophistory_dir\\$date\\index.txt") ){

      while( my $line = <INDEX> ){
        chomp $line; # 改行を削除

        # 履歴データファイル名を取得
        my ($fixed, $filename, $mac_name) = split(/,/, $line);

        if( defined($mac_name) ){
          if( $loom eq $mac_name ){
            push(@file_list,"$stophistory_dir\\$date\\$filename");
            last;
          }
        }
      }
      close(INDEX);
    }
  }

  return @file_list;
}

#####################################################################
