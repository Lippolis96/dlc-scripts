#ifndef DLCGUI_H
#define DLCGUI_H

#include <QMainWindow>

namespace Ui {
class dlcgui;
}

class dlcgui : public QMainWindow
{
    Q_OBJECT

public:
    explicit dlcgui(QWidget *parent = 0);
    ~dlcgui();

private:
    Ui::dlcgui *ui;
};

#endif // DLCGUI_H
