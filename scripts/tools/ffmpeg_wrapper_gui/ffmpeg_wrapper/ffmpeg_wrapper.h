#ifndef FFMPEG_WRAPPER_H
#define FFMPEG_WRAPPER_H

#include <QMainWindow>

namespace Ui {
class FFMPEG_WRAPPER;
}

class FFMPEG_WRAPPER : public QMainWindow
{
    Q_OBJECT

public:
    explicit FFMPEG_WRAPPER(QWidget *parent = 0);
    ~FFMPEG_WRAPPER();

private:
    Ui::FFMPEG_WRAPPER *ui;
};

#endif // FFMPEG_WRAPPER_H
