class BBox:
    in_formats = {
        'x1y1x2y2': lambda x1, y1, x2, y2: ((x1 + x2) / 2, (y1 + y2) / 2, x2 - x1, y2 - y1),
        'x1y1wh': lambda x1, y1, w, h: (x1 + w / 2, y1 + h / 2, w, h),
        'xywh': lambda x, y, w, h: (x, y, w, h)
    }
    out_formats = {
        'x1y1x2y2': lambda x, y, w, h: (x - w / 2, y - h / 2, x + w / 2, y + h / 2),
        'x1x2y1y2': lambda x, y, w, h: (x - w / 2, x + w / 2, y - h / 2, y + h / 2),
        'x1y1wh': lambda x, y, w, h: (x - w / 2, y - h / 2, w, h),
        'xywh': lambda x, y, w, h: (x, y, w, h)
    }

    def __init__(self, **kwargs):
        if 'x1' in kwargs and 'x2' in kwargs and 'y1' in kwargs and 'y2' in kwargs:
            bbox = (kwargs['x1'], kwargs['y1'], kwargs['x2'], kwargs['y2'])
            bbox_format = 'x1y1x2y2'
            self._x, self._y, self._w, self._h = self.in_formats[bbox_format](*bbox)
        elif 'x' in kwargs and 'y' in kwargs and 'w' in kwargs and 'h' in kwargs:
            bbox = (kwargs['x'], kwargs['y'], kwargs['w'], kwargs['h'])
            bbox_format = 'xywh'
            self._x, self._y, self._w, self._h = self.in_formats[bbox_format](*bbox)
        elif 'x1' in kwargs and 'y1' in kwargs and 'w' in kwargs and 'h' in kwargs:
            bbox = (kwargs['x1'], kwargs['y1'], kwargs['w'], kwargs['h'])
            bbox_format = 'x1y1wh'
            self._x, self._y, self._w, self._h = self.in_formats[bbox_format](*bbox)
        else:
            raise ValueError(f"Could not format input {kwargs}")
        keys = {'x1', 'x2', 'y1', 'y2', 'x', 'y', 'w', 'h'}
        self._meta = {key: value for key, value in kwargs.items() if key not in keys}

    def intersects(self, bbox: "BBox") -> bool:
        return self.intersection(bbox) > 0

    def reference(self, x, y):
        x1, y1, w, h = self.x1y1wh
        x1 = x1 - x
        y1 = y1 - y
        bbox = self.in_formats['x1y1wh'](x1, y1, w, h)
        self._x, self._y, self._w, self._h = bbox
        return self

    def iou(self, bbox: "BBox") -> float:
        intersection_area = self.intersection(bbox)
        union_area = self.area() + bbox.area() - intersection_area
        iou = intersection_area / union_area if union_area > 0 else 0
        return iou

    def intersection(self, bbox: "BBox") -> float:
        x1_1, y1_1, x2_1, y2_1 = self.x1y1x2y2
        x1_2, y1_2, x2_2, y2_2 = bbox.x1y1x2y2
        intersection_area = max(0, min(x2_1, x2_2) - max(x1_1, x1_2)) * max(0, min(y2_1, y2_2) - max(y1_1, y1_2))
        return intersection_area

    def area(self):
        x1, y1, x2, y2 = self.x1y1x2y2
        box_area = (x2 - x1) * (y2 - y1)
        return box_area

    def get_intersecting_box(self, bbox: "BBox") -> "BBox":
        x1_1, y1_1, x2_1, y2_1 = self.x1y1x2y2
        x1_2, y1_2, x2_2, y2_2 = bbox.x1y1x2y2
        x1 = max(x1_1, x1_2)
        y1 = max(y1_1, y1_2)
        x2 = min(x2_1, x2_2)
        y2 = min(y2_1, y2_2)
        bbox = {
            'x1': x1,
            'y1': y1,
            'x2': x2,
            'y2': y2,
            **self.meta,
        }
        return BBox(**bbox)

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def w(self):
        return self._w

    @property
    def h(self):
        return self._h

    @property
    def bbox(self):
        return self.x, self.y, self.w, self.h

    @property
    def bbox_dict(self):
        return {'x': self.x, 'y': self.y, 'w': self.w, 'h': self.h}

    @property
    def x1y1x2y2(self):
        return self.out_formats['x1y1x2y2'](*self.bbox)

    @property
    def x1y1wh(self):
        return self.out_formats['x1y1wh'](*self.bbox)

    @property
    def x1x2y1y2(self):
        return self.out_formats['x1x2y1y2'](*self.bbox)

    @property
    def xywh(self):
        return self.out_formats['xywh'](*self.bbox)

    @property
    def meta(self):
        return self._meta

    def __repr__(self):
        return f"{self.bbox}"
