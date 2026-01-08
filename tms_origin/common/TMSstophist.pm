package TMSstophist;

###################################################################################################
#
# TMSstophist.pm
#
###################################################################################################

use strict;
use DirHandle;

use TMSstr;
use TMScommon;

###################################################################################################
# 機能 停台履歴の履歴元フォルダの一覧を返す
# 引数   : なし
# 戻り値 : 履歴元フォルダのパス、履歴元フォルダの配列

sub get_stophist_dir
{
  # 停止履歴データへのパス
  my $stophist_dir = "..\\..\\tmsdata\\stop_history";
  &TMScommon::make_dir( $stophist_dir );

  # サブディレクトリのリスト（データ日付）
  my @stophist_subdir = ();

  my $dir = new DirHandle $stophist_dir;
  if( defined($dir) ){
    my @dir_list = $dir->read;
    $dir->close;

    # yyyy.mm.dd のフォルダ名のみ取得
    foreach( @dir_list ){
      if( ($_ =~ m/^\d{4}\.\d{2}\.\d{2}$/) and
          (-d "$stophist_dir\\$_") ){
        push( @stophist_subdir, $_ );
      }
    }
  }

  return ($stophist_dir, @stophist_subdir);
}

#####################################################################
# 機能   : 要求年月日の停台情報をCSVフォームで所定のフォルダに出力する
#
# 引数   : 進捗表示の PHASE 番号
# 戻り値 : なし

sub make_stophist_csv
{
  my( $phase ) = @_;

  &TMSstr::load_stop_cause(); # 停止原因文字列の読込

  # 履歴元フォルダ一覧の取得
  my ($stophist_dir, @stophist_subdir) = &get_stophist_dir();
  if( $#stophist_subdir < 0 ){ return; }

  # データ作成対象年月日の取得
  my @update_list = ();
  if( open(LST, "< $stophist_dir\\history_update.txt") ){
    while(<LST>){
      chomp;  # 改行を除く
      if( $_ =~ m/^\d{4}\.\d{2}\.\d{2}$/ ){ push(@update_list, $_); }
    }
    close(LST);
  }

  ### CSV出力元ディレクトリ(TMSDATA)を作成 ###
  my $csv_dir = "\\TMSDATA";
  &TMScommon::make_dir($csv_dir);

  ### 経過表示 ###
  my $total = ($#update_list + 1);
  my $count = 0;
  &TMScommon::disp_percent($total, $count, $phase);  # 経過表示（開始）

  foreach my $subdir ( @update_list ){ # yyyy.mm.dd

    &TMScommon::disp_percent($total, ++$count);  # 経過表示（途中）

    # フォルダがなければスキップ
    if( ! -d "$stophist_dir\\$subdir" ){ next; }

    # CSV出力先ディレクトリ(yyyy-mm)を作成
    my @d = split(/\./,$subdir);
    my $yyyy_mm    = "$d[0]-$d[1]";
    my $yyyy_mm_dd = "$d[0]-$d[1]-$d[2]";
    &TMScommon::make_dir("$csv_dir\\$yyyy_mm");
    &TMScommon::make_dir("$csv_dir\\$yyyy_mm\\stop_history");
    &TMScommon::make_dir("$csv_dir\\$yyyy_mm\\stop_history\\$yyyy_mm_dd");

    # 停止履歴フォルダ内のファイル一覧
    my $dir = new DirHandle "$stophist_dir\\$subdir";
    my @file_list = $dir->read;
    $dir->close;

    foreach my $file ( @file_list ){

      # 数字.txt のファイル以外はスキップ
      if( ($file !~ m/^\d+\.txt$/) or
          (! -f "$stophist_dir\\$subdir\\$file") ){ next; }

      # 停止履歴データファイルを読み込む
      if( open(HIST, "< $stophist_dir\\$subdir\\$file") ){

        my $line = <HIST>;  # １行目
        chomp $line;  # 改行を削除

        # day, mac_name, mac_type の値を取得する
        my $day = "";
        my $mac_name = "";
        my $mac_type = "JAT710";  # デフォルト(古いデータで値無しの場合)

        my @item = split(/,/, $line);  # , 区切りで分ける
        foreach( @item ){
          my @col = split(/ /, $_, 2); # スペース区切り
          if( $#col >= 1 ){  # 値があれば
            if( $col[0] eq 'day' ){
              $day = $col[1];  # yyyy.mm.dd
              if( $day =~ m/^\d{4}\.\d{2}\.\d{2}$/ )
                  { $day =~ s/\./\//g; }  # 2005.06.03 -> 2005/06/03
              else{ $day = ""; }
            }
            elsif( $col[0] eq 'mac_name' ){
              $mac_name = $col[1];
            }
            elsif( $col[0] eq 'mac_type' ){
              $mac_type = $col[1];
            }
          }
        }

        # mac_nameの値がある場合だけ
        if( $mac_name ne "" ){

          # ファイル名に使えない文字を変換
          my $csv_fname = $mac_name;
          $csv_fname =~ s/[ \\\/:,;*?"<>|]/_/g;
          $csv_fname .= ".csv";

          # CSVファイルに出力
          if( open CSV, "> $csv_dir\\$yyyy_mm\\stop_history\\$yyyy_mm_dd\\$csv_fname" ){

            # １行目
            # 日付はフォルダの日付でなく、停止履歴ファイルのdayの値を用いる
            print CSV $day.','.$mac_name."\n";

            # ２行目以降
            while( $line = <HIST> ){
              chomp $line; # 改行を除く
              if( length($line) <= 0 ){ next; } # データが無ければスキップ

              ### 停止時刻、運転時刻、停止原因番号 に分解 ###
              my ($stop_time, $run_time, $code) = split( /,/ , $line );
              if( ! defined($code) ){ $code = ""; }

              print CSV $stop_time. ','.
                        $run_time.  ','.
                        &TMSstr::get_stop_cause($code,$mac_type)."\n";
            }
            close(CSV);
          }
        }
        close(HIST);
      }
    }
  }

  &TMScommon::disp_percent(100,101);  # 経過表示（終了）

}

#####################################################################
1;
