classdef TestStateRecovery < matlab.unittest.TestCase
    properties
        RepoRoot
    end

    methods (TestMethodSetup)
        function addToolboxToPath(testCase)
            testCase.RepoRoot = fileparts(fileparts(mfilename('fullpath')));
            addpath(testCase.RepoRoot);
        end
    end

    methods (TestMethodTeardown)
        function removeToolboxFromPath(testCase)
            rmpath(testCase.RepoRoot);
        end
    end

    methods (Test)
        function dx2abcdStable1ForcesStableAAndPredictsWell(testCase)
            [u, y, sys] = testutils.makeSisoData('N', 500, 'seed', 2, 'noiseStd', 0.02);

            f = 5;
            p = 10;

            [~, X] = dordvarx(u, y, f, p);

            n = 1;
            x = dmodx(X, n);

            % Use stability enforcement that does not require Control System Toolbox
            [A, B, C, D] = dx2abcd( x, u, y, f, p, 'stable1');

            % Shape checks for SISO
            testCase.verifySize(A, [n, n]);
            testCase.verifySize(B, [n, 1]);
            testCase.verifySize(C, [1, n]);
            testCase.verifySize(D, [1, 1]);
            
            % Finite checks
            testCase.verifyTrue(all(isfinite(A(:))));
            testCase.verifyTrue(all(isfinite(B(:))));
            testCase.verifyTrue(all(isfinite(C(:))));
            testCase.verifyTrue(all(isfinite(D(:))));

            % Stability check
            testCase.verifyLessThan(max(abs(eig(A))), 1.0);

            % Basic one-step output prediction quality
            % Align with dx2abcd trimming logic: using u(:, p+1:p+size(x,2))
            uRow = u';
            yRow = y';
            uTrim = uRow(:, p+1:p+size(x,2));
            yTrim = yRow(:, p+1:p+size(x,2));

            yHat = C * x + D * uTrim;

            err = yTrim - yHat;
            vaf = 100 * (1 - var(err,1) / var(yTrim, 1));

            % Loose but meaningful threshold, should be comfortably higher on this dataset
            testCase.verifyGreaterThan(vaf, 70);
        end
    end
end